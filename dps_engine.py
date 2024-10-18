"""
DPSEngine module communicates with DPS power supply device through
Modbus protocol
"""

from typing import List, Union, Dict
import minimalmodbus
from minimalmodbus import ModbusException
from serial import SerialException
from enum import IntEnum

# Return codes and messages
class DPSRetCode(IntEnum):
    """Return code enumerations from engine"""
    DPS_OK = 0x0
    DPS_ERROR = 0x1

class DPSRet:
    """Return status class from engine"""
    def __init__(self, code: DPSRetCode, value: str = '',  msg: str = '') -> None:
        self.code = code
        self.value = value
        self.msg = msg

    def get_value(self):
        """Get only the value of return code"""
        return self.value

    def get_message(self):
        """Get only the message of return code"""
        return self.msg

    def __repr__(self) -> str:
        """Representation of return code"""
        return f'code: {self.code}, value: {self.value}, message: {self.msg}'

class DPSRegister(IntEnum):
    """Register addresses of DPS5005"""
    VOLTS_SET = 0x0
    AMPS_SET = 0x1
    VOLTS_OUT = 0x2
    AMPS_OUT = 0x3
    PWR_OUT = 0x4
    VOLTS_UIN = 0x5
    PWR_ONOFF = 0x9

def exception_handler(func):
    """Exception handle for decorator"""
    def inner_function(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except ModbusException:
            print(f"{func.__name__} ModbusException")
        except SerialException:
            print(f"{func.__name__} SerialException")
        except TypeError:
            print(f"{func.__name__} TypeError")
        except ValueError:
            print(f"{func.__name__} ValueError")
    return inner_function

class DPSEngine:
    """Class interacting with DPS5005 through Modbus protocol"""
    def __init__(self, port: str, slave: int, debug : bool = False) -> None:
        """Constructor"""
        self.port = port
        self.instrument = None
        self.slave = slave
        self.debug = debug

    def connect(self) -> DPSRet:
        """Connect to DPS through modbus"""
        try:
            self.instrument = minimalmodbus.Instrument(port=self.port, slaveaddress=self.slave)
        except SerialException as error:
            print(error)
            return DPSRet(DPSRetCode.DPS_ERROR, msg = 'Serial exception')

        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.timeout = 0.5
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.close_port_after_each_call = False
        self.instrument.debug = self.debug
        return DPSRet(DPSRetCode.DPS_OK)

    # Getters and setters
    def set_power(self, enable: bool) -> DPSRet:
        """Switch power output ON/OFF"""
        self.write_register(DPSRegister.PWR_ONOFF, int(enable), 0)
        DPSRet(DPSRetCode.DPS_OK)

    def get_power(self) -> DPSRet:
        """Get current power ON/OFF status"""
        power = self.read_register(DPSRegister.PWR_ONOFF, 0)
        return DPSRet(DPSRetCode.DPS_OK, str(power))

    def toggle_power(self) -> DPSRet:
        """Toggle power ON<->OFF"""
        current_status = self.get_power()
        self.set_power(not current_status)
        return DPSRet(DPSRetCode.DPS_OK)

    def set_volts(self, volts: float) -> DPSRet:
        """Set voltage of DPS device"""
        #TODO: Limit check
        self.write_register(DPSRegister.VOLTS_SET, volts, 2)
        return DPSRet(DPSRetCode.DPS_OK)

    def get_volts_set(self) -> DPSRet:
        """Get set value of volts out, not necessary the actual out voltage atm"""
        volts = self.read_register(DPSRegister.VOLTS_SET, 2)
        return DPSRet(DPSRetCode.DPS_OK, str(volts))

    def get_volts_out(self) -> DPSRet:
        """Get voltage output at the moment"""
        volts = self.read_register(DPSRegister.VOLTS_OUT, 2)
        return DPSRet(DPSRetCode.DPS_OK, str(volts))

    def set_amps(self, amps: float) -> DPSRet:
        """Set current of DPS device"""
        #TODO: Limit check
        self.write_register(DPSRegister.AMPS_SET, amps, 3)
        return DPSRet(DPSRetCode.DPS_OK)

    def get_amps_set(self) -> DPSRet:
        """Get set value of amps out, not necessary the actual out current atm"""
        volts = self.read_register(DPSRegister.AMPS_SET, 3)
        return DPSRet(DPSRetCode.DPS_OK, str(volts))

    def get_amps_out(self) -> DPSRet:
        """Get current output at the moment"""
        amps = self.read_register(DPSRegister.AMPS_OUT, 3)
        return DPSRet(DPSRetCode.DPS_OK, str(amps))

    def get_power_out(self) -> DPSRet:
        """Get current power output"""
        power = self.read_register(DPSRegister.PWR_OUT, 2)
        return DPSRet(DPSRetCode.DPS_OK, str(power))

    def get_status(self) -> List[int]:
        """Get dump of status variables of DPS, 20 registers starting from 0x0"""
        b = self.read_registers(0x0, 20)
        return b

    # Communication through Modbus, catch exceptions on these, used internally by class
    @exception_handler
    def write_register(self, address: int, value: Union[int,float], num_decimals: int) -> None:
        """Write single register at at address"""
        self.instrument.write_register(address, value=value, number_of_decimals=num_decimals)
        print('Write register')

    @exception_handler
    def write_registers(self, address: int, values: List[int]) -> None:
        """Write list of registers into address"""
        self.instrument.write_registers(registeraddress=address, values=values)

    @exception_handler
    def read_register(self, address: int, num_decimals: int) -> Union[int, float]:
        """Read single register from address"""
        retval = self.instrument.read_register(address, num_decimals)
        return retval

    @exception_handler
    def read_registers(self, address: int, number: int) -> List[int]:
        """Read number of registers starting from address"""
        registers = self.instrument.read_registers(registeraddress=address,
                                                   number_of_registers=number)
        return registers

    # Utilities
    def get_status_string(self) -> Dict[str, float]:
        """Get dictionary representation of status byte dump"""
        b = self.get_status()
        if len(b) != 20:
            print('Invalid status response from DPS device')
            return
        st =  { 'U-Set': b[0] / 100.0,
                'I-Set': b[1] / 1000.0,
                'U-Out': b[2] / 100.0,
                'I-Out': b[3] / 1000.0,
                'P-Out': b[4] / 100.0,
                'U-In': b[5] / 100.0,
                'Locked': {0: 'OFF', 1: 'ON'}.get(b[6]),
                'Protected': {0: 'ON', 1: 'OFF'}.get(b[7]),
                'CV/CC': {0: 'CV', 1: 'CC'}.get(b[8]),
                'ON_OFF': {0: 'OFF', 1: 'ON'}.get(b[9]),
                'Backlight': b[10],
                'Model': str(b[11]),
                'Firmware': str(b[12] / 10.0),
        }
        return st

if __name__ == "__main__":
    print('DPSEngine is not meant to be run standalone')
