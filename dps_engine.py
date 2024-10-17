"""
DPSEngine module communicates with DPS power supply device through
Modbus protocol
"""

from typing import List, Union, Dict
import minimalmodbus
from minimalmodbus import ModbusException
from serial import SerialException
from enum import IntEnum
from dps_status import DPSRegisters

class DPSRegister(IntEnum):
    """Register addresses of DPS5005"""
    VOLTS_SET = 0x0
    AMPS_SET = 0x1
    VOLTS_OUT = 0x2
    AMPS_OUT = 0x3
    PWR_OUT = 0x4
    VOLTS_UIN = 0x5
    PWR_ONOFF = 0x9

# def exception_handler(func):
#     """Exception handle for decorator"""
#     def inner_function(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except ModbusException:
#             print(f"{func.__name__} ModbusException")
#         except SerialException:
#             print(f"{func.__name__} SerialException")
#         except TypeError:
#             print(f"{func.__name__} TypeError")
#         except ValueError:
#             print(f"{func.__name__} ValueError")
#     return inner_function

class DPSEngine:
    """Class interacting with DPS5005 through Modbus protocol"""
    def __init__(self, debug : bool = False) -> None:
        """Constructor"""
        self.registers = DPSRegisters()
        self.instrument = None
        self.debug: bool = debug

    def connect(self, port: str, slave: int) -> tuple[bool, str]:
        """Connect to DPS through modbus"""
        try:
            self.instrument = minimalmodbus.Instrument(port, slave)
        except SerialException as error:
            print(error)
            return (False, 'Serial exception')

        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.timeout = 0.5
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.close_port_after_each_call = False
        self.instrument.debug = self.debug
        self.set_power(False)
        return (True, '')

    # Getters and setters
    def set_power(self, enable: bool) -> tuple[bool, str]:
        """Set current power ON/OFF status"""
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

    def get_printable_status(self) -> tuple[bool, str]:
        """Get dump of status variables of DPS"""
        # TODO: Move to DPSStatus() __repr__ __str__?
        retstr = str()
        retstr += f'U-Set:\t\t{self.registers[0] / 100.0}\n'
        retstr += f'I-Set:\t\t{self.registers[1] / 1000.0}\n'
        retstr += f'U-Out:\t\t{self.registers[2] / 100.0}\n'
        retstr += f'I-Out:\t\t{self.registers[3] / 1000.0}\n'
        retstr += f'P-Out:\t\t{self.registers[4] / 100.0}\n'
        retstr += f'U-In:\t\t{self.registers[5] / 100.0}\n'
        retstr += f'Locked:\t\t{self.registers[6]}\n'
        retstr += f'Protected:\t{self.registers[7]}\n'
        retstr += f'CV/CC:\t\t{self.registers[8]}\n'
        retstr += f'ONOFF:\t\t{self.registers[9]}\n'
        retstr += f'Backlight:\t{self.registers[10]}\n'
        retstr += f'Model:\t\t{self.registers[11]}\n'
        retstr += f'Firmware:\t{self.registers[12] / 10.0}\n'
        return (True, retstr)

    def get_registers(self) -> DPSRegisters:
        """Get status registers from DPS device"""
        reglist: Lis[int] = self.__read_registers(0x0, 20)
        if len(registers != 20):
            return None
        reg: DPSRegisters = self.registers
        reg.u_set = reglist[0]
        reg.i_set = reglist[1]
        reg.u_out = reglist[2]
        reg.i_out = reglist[3]
        reg.p_out = reglist[4]
        reg.u_in = reglist[5]
        reg.lock = reglist[6]
        reg.protect = reglist[7]
        reg.cvcc = reglist[8]
        reg.model = reglist[9]
        reg.version = reglist[10]
        return reg

    # Private methods
    # Communication through Modbus, catch exceptions on these, used internally by class
    def __write_register(self, address: int, value: Union[int,float], num_decimals: int) -> None:
        """Write single register at at address"""
        self.instrument.write_register(address, value=value, number_of_decimals=num_decimals)

    def __write_registers(self, address: int, values: List[int]) -> None:
        """Write list of registers into address"""
        self.instrument.write_registers(registeraddress=address, values=values)

    def __read_register(self, address: int, num_decimals: int) -> Union[int, float]:
        """Read single register from address"""
        retval: int | float = self.instrument.read_register(address, num_decimals)
        return retval

    def __read_registers(self, address: int, number: int) -> List[int]:
        """Read number of registers starting from address"""
        regs : List[int] = self.instrument.read_registers(registeraddress=address,
                                                   number_of_registers=number)
        return regs

if __name__ == "__main__":
    print('DPSEngine is not meant to be run standalone')
