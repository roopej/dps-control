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
Set voltage and current     va <float> <float>
Info:                       i
Power set/toggle ON/OFF:    x [0/1]
Monitor toggle ON/OFF:      m

"""

import threading
from typing import Callable
from queue import SimpleQueue
from time import sleep

from lib.dps_status import DPSStatus
from lib.dps_engine import DPSEngine
from lib.utils import *

VERSION: str = '0.2'

class DPSController:
    """Handles logic and parsing commands"""
    def __init__(self, conf) -> None:
        self.status: DPSStatus = DPSStatus()
        self.conf = conf
        self.status.port = conf['connection']['tty_port']
        self.status.slave = conf['connection']['slave']
        self.status.baud_rate = conf['connection']['baud_rate']
        self.event_queue: SimpleQueue = SimpleQueue()
        self.event_thread : threading.Thread

        # Instance to talk to DPS device through Modbus
        self.engine = DPSEngine(debug = False)
        self.version: str = VERSION

        # Limits from configuration
        self.v_max = self.conf['limits']['max_voltage']
        self.v_min = self.conf['limits']['min_voltage']
        self.a_max = self.conf['limits']['max_current']
        self.a_min = self.conf['limits']['min_current']

    @staticmethod
    def get_version() -> str:
        """Get version string"""
        return VERSION

    def get_port(self) -> str:
        """Get port as string"""
        return self.status.port

    def get_slave(self) -> str:
        """Get slave number as string"""
        return str(self.status.slave)

    def get_baud_rate(self) -> str:
        """Get baud rate as string"""
        return str(self.status.baudrate)

    def connect(self) -> tuple[bool, str]:
        """Start controller, connect to device"""
        conn, msg = self.engine.connect(self.status.port, self.status.slave, self.status.baudrate)
        if not conn:
            return False, "ERROR: Cannot connect to DPS device."

        self.status.connected = True
        self.get_status()

        # If configured, start with power off always
        if self.conf['misc']['start_power_off']:
            self.engine.set_power(False)
            self.status.registers.onoff = 0

        self.start_events()
        return True, "Connection successful"

    def get_portinfo(self) -> tuple[bool, str]:
        """Convenience method to get just the port info"""
        return (
            True,
            f'Connected:\t{self.status.connected}\nPort:\t\t{self.status.port}\nSlave:\t\t{self.status.slave}',
        )

    def get_connected(self) -> bool:
        """Get connected status"""
        return self.status.connected

    def get_power_state(self) -> int:
        """Get output power status"""
        return self.status.registers.onoff

    def get_status(self) -> DPSStatus:
        """Get status of controller and DPS device"""
        # Update registers
        self.status.registers = self.engine.get_registers()
        return self.status

    def get_vmax(self) -> float:
        """Get max voltage from configuration"""
        return self.v_max

    def get_vmin(self) -> float:
        """Get min voltage from configuration"""
        return self.v_min

    def get_amax(self) -> float:
        """Get max current from configuration"""
        return self.a_max

    def get_amin(self) -> float:
        """Get min current from configuration"""
        return self.a_min

    def __event_provider(self) -> None:
        """Event provider thread filling up the event queue"""
        while True:
            status: DPSStatus = DPSStatus()
            registers : dict[str, any] = self.engine.get_registers()
            status.registers = registers
            self.event_queue.put_nowait(status)
            sleep(1)

    def start_events(self) -> None:
        """Start a thread providing events from DPS"""
        self.event_thread = threading.Thread(target=self.__event_provider, args=(), daemon=True)
        self.event_thread.start()

    def stop_events(self) -> None:
        """Stop producing events by inserting None event"""
        self.event_queue.put_nowait(None)

    def parse_command(self, cmd: str) -> tuple[bool, str]:
        """Parse input command and act upon it. Return false if quit requested"""
        # print(f'Parser got: {cmd}')
        # Special case for quitting program
        if cmd == 'q':
            self.stop_events()
            return True, 'Quit requested'

        # Tuple containing handler information
        execute: tuple[Callable, str, bool] = self.__get_cmd_and_validate(cmd)

        # If command requires connection and we are not connected
        if bool(execute[2]) and not self.status.connected:
            return (
                False,
                'This command requires connection to DPS device. Use the \'c\' command to connect first.',
            )

        # If no callback was parsed
        if execute[0] is None:
            return False, 'Invalid command'

        # Execute
        ret = execute[0](execute[1])
        print(ret)
        return ret

    # Private methods
    def __get_args(self, cmd: str, num: int):
        """Get num of arguments for command, ignore extras"""
        return ' '.join(cmd.split()[0:num])

    def __handle_connect(self, cmd) -> tuple[bool, str]:
        """Handle connect command"""

        # Ignore extra arguments
        args = self.__get_args(cmd, 1)
        if self.status.connected:
            return False, 'Already connected'
        if len(cmd):
            self.status.port = args
        return self.connect()

    def __handle_info(self, cmd) -> tuple[bool, str]:
        """Handle info command"""
        return self.engine.get_printable_status()

    def __handle_power_switch(self, pwr) -> tuple[bool, str]:
        """Handle power on/off and toggle commands, toggle if specific argument"""
        switchto: bool
        if len(pwr) == 0:
            switchto = not self.status.registers.onoff
        else:
            switchto = bool(pwr)

        self.engine.set_power(switchto)
        self.status.registers.onoff = switchto
        pwr = 'ON' if switchto is True else 'OFF'
        return True, f'Power switched {pwr}'

    def __handle_set_port(self, port) -> tuple[bool, str]:
        """Handle set port"""
        if len(port) == 0:
            return False, 'Port argument is required'
        self.status.port = port
        return True, f'Port set to {port}'

    def __check_volts_range(self, volts: float) -> bool:
        """Check that requested volts are within configured limits"""
        if self.v_max >= volts >= self.v_min:
            return True
        return False

    def __check_amps_range(self, amps: float) -> bool:
        """Check that requested amps are within configured limits"""
        if self.a_max >= amps >= self.a_min:
            return True
        return False

    def __handle_set_volts(self, args) -> tuple[bool, str]:
        """Function to handle set volts command"""
        if validate_float(args):
            volts = float(args)
            if not self.__check_volts_range(volts):
                return False, f'Voltage requested out of configured limits [{volts}]'
            ret, msg = self.engine.set_volts(volts)
            if not ret:
                return False, 'Set volts failed'
            return True, 'Success'

    def __handle_set_amps(self, args) -> tuple[bool, str]:
        """Function to handle set amps command"""
        if validate_float(args):
            amps = float(args)
            if not self.__check_amps_range(amps):
                return False, f'Current requested out of configured limits [{amps}]'
            ret, msg = self.engine.set_amps(amps)
            if not ret:
                return False, 'Set amps failed'
            return True, 'Success'

    def __handle_set_volts_and_amps(self, args) -> tuple[bool, str]:
        """Function to handle set volts command"""
        if len(args.split()) < 2:
            return False, 'Invalid values'
        volts: str = args.split()[0]
        amps: str = args.split()[1]
        if validate_float(volts) and validate_float(amps):
            a = float(amps)
            v = float(volts)

            if not self.__check_amps_range(a) or not self.__check_volts_range(v):
                return False, f'Voltage or current requested out of configured limits [{v} V, {a} A]'

            ret, msg = self.engine.set_volts_and_amps(float(volts), float(amps))
            if not ret:
                return False, 'Set volts failed'
            return True, f'Success: set volts to {v} and amps to {a}'
        else:
            print('Invalid values')

    def __get_cmd_and_validate(self, cmd: str) -> tuple[Callable or None, str, bool]:
        """Get command handler and validate args"""
        main_cmd = cmd.split()[0].lower()
        # Get args if available
        args: str = ' '.join(cmd.split()[1:])

        # Commands to handle (handler, arguments, connection_required)
        if main_cmd == 'c':
            return self.__handle_connect, args, False
        elif main_cmd == 'p':
            return self.__handle_set_port, args, False
        elif main_cmd == 'v':
            return self.__handle_set_volts, args, True
        elif main_cmd == 'va':
            return self.__handle_set_volts_and_amps, args, True
        elif main_cmd == 'a':
            return self.__handle_set_amps, args, True
        elif main_cmd == 'i':
            return self.__handle_info, args, True
        elif main_cmd == 'x':
            return self.__handle_power_switch, args, True
        else:
            return None, '', False
