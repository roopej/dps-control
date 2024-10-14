"""
DPSEngine module communicates with DPS power supply device through
Modbus protocol
"""

from typing import List, Union, Dict
import minimalmodbus
from minimalmodbus import ModbusException
from serial import SerialException
from enum import IntEnum

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
        self.port: str = port
        self.instrument = None
        self.slave: int = slave
        self.debug: bool = debug

    def connect(self) -> tuple[bool, str]:
        """Connect to DPS through modbus"""
        try:
            self.instrument = minimalmodbus.Instrument(port=self.port, slaveaddress=self.slave)
        except SerialException as error:
            print(error)
            return (False, 'Serial exception')

        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.timeout = 0.5
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.close_port_after_each_call = False
        self.instrument.debug = self.debug
        return (True, '')

    # Getters and setters
    def set_power(self, enable: bool) -> tuple[bool, str]:
        """Switch power output ON/OFF"""
        self.__write_register(DPSRegister.PWR_ONOFF, int(enable), 0)
        return (True, '')

    def get_power(self) -> tuple[bool, str]:
        """Get current power ON/OFF status"""
        power: float = self.__read_register(DPSRegister.PWR_ONOFF, 0)
        return (True, str(power))

    def toggle_power(self) -> tuple[bool, str]:
        """Toggle power ON<->OFF"""
        current_status: tuple[bool, str] = self.get_power()
        toggle: bool = current_status[1] == 'True'
        self.set_power(not toggle)
        return (True, '')

    def set_volts(self, volts: float) -> tuple[bool, str]:
        """Set voltage of DPS device"""
        #TODO: Limit check
        self.__write_register(DPSRegister.VOLTS_SET, volts, 2)
        return (True, '')

    def get_volts_set(self) -> tuple[bool, str]:
        """Get set value of volts out, not necessary the actual out voltage atm"""
        volts: int | float = self.__read_register(DPSRegister.VOLTS_SET, 2)
        return (True, str(volts))

    def get_volts_out(self) -> tuple[bool, str]:
        """Get voltage output at the moment"""
        volts: int | float = self.__read_register(DPSRegister.VOLTS_OUT, 2)
        return (True, str(volts))

    def set_amps(self, amps: float) -> tuple[bool, str]:
        """Set current of DPS device"""
        #TODO: Limit check
        self.__write_register(DPSRegister.AMPS_SET, amps, 3)
        return (True, '')

    def get_amps_set(self) -> tuple[bool, str]:
        """Get set value of amps out, not necessary the actual out current atm"""
        volts: int | float = self.__read_register(DPSRegister.AMPS_SET, 3)
        return (True, str(volts))

    def get_amps_out(self) -> tuple[bool, str]:
        """Get current output at the moment"""
        amps: int | float = self.__read_register(DPSRegister.AMPS_OUT, 3)
        return (True, str(amps))

    def get_power_out(self) -> tuple[bool, str]:
        """Get current power output"""
        power: int | float = self.__read_register(DPSRegister.PWR_OUT, 2)
        return (True, str(power))

    def get_status(self) -> tuple[bool, str]:
        """Get dump of status variables of DPS, 20 registers starting from 0x0"""
        registers: List[int] = self.__read_registers(0x0, 20)
        if len(registers) != 20:
            return (False, 'Error reading DPS registers')

        retstr = str()
        retstr += f'U-Set:\t\t{registers[0] / 100.0}\n'
        retstr += f'I-Set:\t\t{registers[1] / 1000.0}\n'
        retstr += f'U-Out:\t\t{registers[2] / 100.0}\n'
        retstr += f'I-Out:\t\t{registers[3] / 1000.0}\n'
        retstr += f'P-Out:\t\t{registers[4] / 100.0}\n'
        retstr += f'U-In:\t\t{registers[5] / 100.0}\n'
        retstr += f'Locked:\t\t{registers[6]}\n'
        retstr += f'Protected:\t{registers[7]}\n'
        retstr += f'CV/CC:\t\t{registers[8]}\n'
        retstr += f'ONOFF:\t\t{registers[9]}\n'
        retstr += f'Backlight:\t\t{registers[10]}\n'
        retstr += f'Model:\t\t{registers[11]}\n'
        retstr += f'Firmware:\t{registers[12]}\n'

        return (True, retstr)

    # Private methods
    # Communication through Modbus, catch exceptions on these, used internally by class
    @exception_handler
    def __write_register(self, address: int, value: Union[int,float], num_decimals: int) -> None:
        """Write single register at at address"""
        self.instrument.write_register(address, value=value, number_of_decimals=num_decimals)

    @exception_handler
    def __write_registers(self, address: int, values: List[int]) -> None:
        """Write list of registers into address"""
        self.instrument.write_registers(registeraddress=address, values=values)

    @exception_handler
    def __read_register(self, address: int, num_decimals: int) -> Union[int, float]:
        """Read single register from address"""
        retval: int | float = self.instrument.read_register(address, num_decimals)
        return retval

    @exception_handler
    def __read_registers(self, address: int, number: int) -> List[int]:
        """Read number of registers starting from address"""
        registers: List[int] = self.instrument.read_registers(registeraddress=address,
                                                   number_of_registers=number)
        return registers

if __name__ == "__main__":
    print('DPSEngine is not meant to be run standalone')
