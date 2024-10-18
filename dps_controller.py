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
from typing import Callable
from dps_state import DPSState
from dps_engine import DPSEngine
import dps_config as conf

class DPSController:
    """Handles logic and parsing commands"""
    def __init__(self) -> None:
        # Model, read some values from config
        self.dps_state : DPSState = DPSState()
        self.dps_state.port = conf.ttyPort
        self.dps_state.slave = conf.slave
        self.dps_state.min_amps = conf.min_current
        self.dps_state.max_amps = conf.max_current
        self.dps_state.min_volts = conf.min_voltage
        self.dps_state.max_volts = conf.max_voltage

        # Instance to talk to DPS device through Modbus
        self.dps_engine = DPSEngine(self.dps_state.port, self.dps_state.slave)

    def connect(self) -> tuple[bool,str]:
        """Start controller, connect to device"""
        conn: tuple[bool, str] =  self.dps_engine.connect()
        if not conn[0]:
            return False, 'ERROR: Cannot connect to DPS device.'
        return True, 'Connection successful'

    def get_state(self) -> tuple[bool,str]:
        """Print state of DPS device"""
        return True, str(self.dps_state)

    def get_portinfo(self) -> tuple[bool,str]:
        """Convenience method to get just the port info"""
        st: DPSState = self.dps_state
        return True , f'Connected:\t{st.connected}\nPort:\t\t{st.port}\nSlave:\t\t{st.slave}'

    def parse_command(self, cmd: str) -> tuple[bool,str]:
        """Parse input command and act upon it. Return false if quit requested"""

        # Special case for quitting program
        if cmd == 'q':
            return (True, 'Quit requested')

        # Tuple containing handler information
        execute: tuple[Callable, str, bool] = self.__get_cmd_and_validate(cmd)

        # If command requires connection and we are not connected
        if bool(execute[2]) and not self.dps_state.connected:
            return (False, 'You are not connected.')

        # If no callback was parsed
        if execute[0] is None:
            return (False, 'Invalid command')

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
        if len(cmd.split()) > 1:
            self.dps_state.port = cmd.split()[1]
        return self.connect()

    def __handle_info(self, cmd) -> tuple[bool, str]:
        return self.dps_engine.get_status

    def __handle_set_port(self, port) -> tuple[bool, str]:
        """Handle set port"""
        if len(port) == 0:
            return (False, 'Port argument is required')

        self.dps_state.port = port
        return (True, f'Port set to {port}')

    def __handle_set_volts(self, args) -> tuple[bool, str]:
        """Function to handle set volts command"""
        if self.__validate_float(args):
            ret: tuple[bool, str] = self.dps_engine.set_volts(float(args))
            if not ret[0]:
                return (False, 'Set volts failed')
            return (True, 'Success')

    def __handle_set_amps(self, args) -> tuple[bool, str]:
        """Function to handle set amps command"""
        if self.__validate_float(args):
            ret: tuple[bool, str] = self.dps_engine.set_amps(float(args))
            if not ret[0]:
                return (False, 'Set amps failed')
            return (True, 'Success')

    def __get_cmd_and_validate(self, cmd: str) -> tuple[Callable,str,bool]:
        """Get command handler and validate args"""
        main_cmd = cmd.split()[0].lower()

        # Get args if available
        args = str()
        if len(cmd.split()) > 1:
            args: str = cmd.split()[1]

        if main_cmd == 'c':
            return (self.__handle_connect, args, False)
        elif main_cmd == 'p':
            return (self.__handle_set_port, args, False)
        elif main_cmd == 'v':
            return (self.__handle_set_volts, args, True)
        elif main_cmd == 'a':
            return (self.__handle_set_amps, args, True)
        elif main_cmd == 'i':
            return (self.__handle_info, args, True)
        else:
            return (None, '', False)
