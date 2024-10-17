"""
Controller class for DPS control
Owns the DPS state class and takes input commands
as ASCII strings, like "a 4.5" which sets current to 4.5A

Return values for public methods are generally in tuple[bool, str]
format, where bool is success code and str is description

Commands supported:
===================

Connect:                    c [<port>]
Set port:                   p <port>
Set voltage:                v <float>
Set current:                a <float>
Info:                       i
Power set/toggle ON/OFF:    x [0/1]
Monitor toggle ON/OFF:      m

"""

import threading
from typing import Callable
from queue import SimpleQueue
from time import sleep

from dps_status import DPSStatus
from dps_engine import DPSEngine
#import dps_config as conf

# Global flag for stopping producing events
STOP_EVENTS: bool = False
VERSION: str = '0.2'

class DPSController:
    """Handles logic and parsing commands"""
    def __init__(self, port: str, slave: int, events: SimpleQueue = None) -> None:
        self.status: DPSStatus = DPSStatus()
        self.status.port = port
        self.status.slave = slave
        self.event_queue: SimpleQueue = events
        self.event_thread : threading.Thread = None

        # Instance to talk to DPS device through Modbus
        self.engine = DPSEngine(debug = False)
        self.version: str = VERSION

    @staticmethod
    def get_version() -> str:
        """Get version string"""
        return VERSION

    def connect(self) -> tuple[bool, str]:
        """Start controller, connect to device"""
        conn: tuple[bool, str] = self.engine.connect(self.status.port, self.status.slave)
        if not conn[0]:
            return False, "ERROR: Cannot connect to DPS device."

        self.status.connected = True
        return True, "Connection successful"

    # def get_state(self) -> tuple[bool, str]:
    #     """Print state of DPS device"""
    #     return True, str(self.status)

    def get_portinfo(self) -> tuple[bool, str]:
        """Convenience method to get just the port info"""
        return (
            True,
            f"Connected:\t{self.status.connected}\nPort:\t\t{self.status.port}\nSlave:\t\t{self.status.slave}",
        )

    def get_connected(self) -> bool:
        """Get connected status"""
        return self.status.connected

    def get_power_state(self) -> bool:
        """Get output power status"""
        return self.status.registers.onoff

    def get_status(self) -> DPSStatus:
        """Get status of controller and DPS device"""
        # Update registers
        self.status.registers = self.engine.get_registers()
        return self.status

    def __event_provider(self) -> None:
        """Event provider thread filling up the event queue"""
        global STOP_EVENTS
        STOP_EVENTS = False
        running = True
        while running:
            #registers : dict[str, any] = self.engine.get_status()
            #self.event_queue.put_nowait(registers)
            if STOP_EVENTS:
                running = False
            sleep(1)

    def start_events(self) -> None:
        """Start a thread providing events from DPS"""
        self.event_thread = threading.Thread(target=self.__event_provider, args=())
        self.event_thread.start()

    def stop_events(self) -> None:
        """Stop producing events"""
        global STOP_EVENTS
        STOP_EVENTS = True

    def parse_command(self, cmd: str) -> tuple[bool, str]:
        """Parse input command and act upon it. Return false if quit requested"""

        # Special case for quitting program
        if cmd == "q":
            return (True, "Quit requested")

        # Tuple containing handler information
        execute: tuple[Callable, str, bool] = self.__get_cmd_and_validate(cmd)

        # If command requires connection and we are not connected
        if bool(execute[2]) and not self.status.connected:
            return (
                False,
                "This command requires connection to DPS device. Use the 'c' command to connect first.",
            )

        # If no callback was parsed
        if execute[0] is None:
            return (False, "Invalid command")

        # Execute
        return execute[0](execute[1])

    # Private methods
    def __validate_float(self, value) -> bool:
        """Check if string can be interpreted as float"""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def __validate_int(self, value) -> bool:
        """Check if string can be interpreted as int"""
        try:
            int(value)
            return True
        except ValueError:
            return False

    def __handle_connect(self, cmd) -> tuple[bool, str]:
        """Handle connect command"""
        if self.status.connected:
            return (False, 'Already connected')
        if len(cmd):
            self.status.port = cmd
        return self.connect()

    def __handle_info(self, cmd) -> tuple[bool, str]:
        """Handle info command"""
        return self.engine.get_printable_status()

    def __handle_power_switch(self, pwr) -> tuple[bool, str]:
        """Handle power on/off and toggle commands, toggle if specific argument"""
        switchto: bool = False
        if len(pwr) == 0:
            switchto = not self.status.registers.onoff
        else:
            switchto = bool(pwr)

        self.engine.set_power(switchto)
        self.status.registers.onoff = switchto
        pwr = 'ON' if switchto is True else 'OFF'
        return (True, f'Power switched {pwr}')

    def __handle_set_port(self, port) -> tuple[bool, str]:
        """Handle set port"""
        if len(port) == 0:
            return (False, "Port argument is required")
        self.status.port = port
        return (True, f"Port set to {port}")

    def __handle_set_volts(self, args) -> tuple[bool, str]:
        """Function to handle set volts command"""
        if self.__validate_float(args):
            ret: tuple[bool, str] = self.engine.set_volts(float(args))
            if not ret[0]:
                return (False, "Set volts failed")
            return (True, "Success")

    def __handle_set_amps(self, args) -> tuple[bool, str]:
        """Function to handle set amps command"""
        if self.__validate_float(args):
            ret: tuple[bool, str] = self.engine.set_amps(float(args))
            if not ret[0]:
                return (False, "Set amps failed")
            return (True, "Success")

    def __get_cmd_and_validate(self, cmd: str) -> tuple[Callable, str, bool]:
        """Get command handler and validate args"""
        main_cmd = cmd.split()[0].lower()

        # Get args if available
        args = str()
        if len(cmd.split()) > 1:
            args: str = cmd.split()[1]

        # Commands to handle (handler, arguments, connection_required)
        if main_cmd == "c":
            return (self.__handle_connect, args, False)
        elif main_cmd == "p":
            return (self.__handle_set_port, args, False)
        elif main_cmd == "v":
            return (self.__handle_set_volts, args, True)
        elif main_cmd == "a":
            return (self.__handle_set_amps, args, True)
        elif main_cmd == "i":
            return (self.__handle_info, args, True)
        elif main_cmd == "x":
            return (self.__handle_power_switch, args, True)
        else:
            return (None, "", False)
