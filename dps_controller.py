"""
Controller class for DPS control
Owns the DPS state class and takes input commands
as ASCII strings, like "a 4.5" which sets current to 4.5A

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
from dps_engine import DPSEngine, DPSRet, DPSRetCode
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

    def connect(self) -> bool:
        """Start controller, connect to device"""
        conn : DPSRet =  self.dps_engine.connect()
        if not conn.code  == DPSRetCode.DPS_OK:
            print('ERROR: Cannot connect to DPS device. ' +
                  'Please check your port and slave configuration.')
            return False
        return True

    def print_state(self) -> None:
        """Print state of DPS device"""
        print(self.dps_state)

    def get_portinfo(self) -> None:
        """Print port information"""
        return self.dps_state.get_portinfo()

    def handle_connect(self, cmd) -> bool:
        """Handle connect command"""
        if len(cmd.split()) > 1:
            self.dps_state.port = cmd.split()[1]
            self.connect()
        return True

    def handle_set_port(self, port) -> bool:
        """Handle set port"""
        print(len(port))
        if len(port) == 0:
            return False

        self.dps_state.port = port
        return True

    def validate_float(self, value) -> bool:
        """Check if string can be interpreted as float"""
        try:
            float(value)
            return True
        except ValueError:
            return False

    def validate_int(self, value) -> bool:
        """Check if string can be interpreted as int"""
        try:
            int(value)
            return True
        except ValueError:
            return False

    def handle_set_volts(self, args) -> bool:
        """Function to handle set volts command"""
        if self.validate_float(args):
            ret = self.dps_engine.set_volts(float(args))
            if not ret.code == DPSRetCode.DPS_OK:
                return False
            return True

    def handle_set_amps(self, args) -> bool:
        """Function to handle set amps command"""
        if self.validate_float(args):
            ret = self.dps_engine.set_amps(float(args))
            if not ret.code == DPSRetCode.DPS_OK:
                return False
            return True

    def get_cmd_and_validate(self, cmd: str) -> tuple[Callable,str,bool]:
        """Get command handler and validate args

        Args:
            cmd (str): Command string

        Returns:
            tuple[Callable,str,bool]: (handler, args, requires_connection)
        """
        main_cmd = cmd.split()[0].lower()

        # Get args if available
        args = str()
        if len(cmd.split()) > 1:
            args = cmd.split()[1]

        if main_cmd == 'c':
            return (self.handle_connect, args, False)
        elif main_cmd == 'p':
            return (self.handle_set_port, args, False)
        elif main_cmd == 'v':
            return (self.handle_set_volts, args, True)
        elif main_cmd == 'a':
            return (self.handle_set_amps, args, True)
        else:
            return (None, '', False)

    def parse_command(self, cmd: str) -> tuple[bool,str]:
        """Parse input command and act upon it. Return false if quit requested"""
        print(f'Parser received: {cmd}')

        # Special case for quitting program
        if cmd == 'q':
            return (False, 'Quit requested')

        # Tuple containing handler information
        execute = self.get_cmd_and_validate(cmd)

        # If command requires connection and we are not connected
        if bool(execute[2]) and not self.dps_state.connected:
            return (True, 'You are not connected.')

        if execute[0] is None:
            return (True, 'Invalid command')

        # Execute
        ret = execute[0](execute[1])

        if ret:
            return (True, 'Success')

        return (True, 'Failure')

