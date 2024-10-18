"""Controller class for DPS control"""
from dps_state import DPSState
from dps_engine import DPSEngine
import dps_config as conf

class DPSController:
    """Handles logic and parsing commands"""
    def __init__(self) -> None:
        self.dps_state : DPSState = DPSState()
        self.dps_state.port = conf.ttyPort
        self.dps_state.slave = conf.slave
        self.dps_state.min_amps = conf.min_current
        self.dps_state.max_amps = conf.max_current
        self.dps_state.min_volts = conf.min_voltage
        self.dps_state.max_volts = conf.max_voltage
        self.dps_engine = DPSEngine(self.dps_state.port, self.dps_state.slave)

    def connect(self) -> bool:
        """Start controller, connect to device"""
        if not self.dps_engine.connect():
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

    def parse_command(self, cmd: str) -> bool:
        """Parse input command and act upon it. Return false if quit requested"""
        print(f'Parser received: {cmd}')
        if cmd == 'c':
            self.connect()
        elif cmd == 'q':
            return False
        return True

