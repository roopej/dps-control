"""
DPSEngine module communicates with DPS power supply device through
Modbus protocol
"""

from typing import List, Union
import minimalmodbus
from minimalmodbus import ModbusException, NoResponseError
from serial import SerialException
from enum import IntEnum
from .dps_status import DPSRegisters

# Converters from int -> float
from .utils import iampsf, ivoltsf, iwattsf

class DPSRegister(IntEnum):
    """Register addresses of DPS5005"""
    VOLTS_SET = 0x0
    AMPS_SET = 0x1
    VOLTS_OUT = 0x2
    AMPS_OUT = 0x3
    PWR_OUT = 0x4
    VOLTS_UIN = 0x5
    PWR_ONOFF = 0x9
    MODEL = 0x0B

class DPSEngine:
    """Class interacting with DPS5005 through Modbus protocol"""
    def __init__(self, debug : bool = False) -> None:
        """Constructor"""
        self.registers = DPSRegisters()
        self.instrument: minimalmodbus.Instrument
        self.debug: bool = debug

    def connect(self, port: str, slave: int, baud_rate: int) -> tuple[bool, str]:
        """Connect to DPS through modbus"""
        try:
            self.instrument = minimalmodbus.Instrument(port, slave)
            self.instrument.serial.baudrate = baud_rate
            self.instrument.serial.bytesize = 8
            self.instrument.serial.timeout = 0.5
            self.instrument.mode = minimalmodbus.MODE_RTU
            self.instrument.close_port_after_each_call = False
            self.instrument.debug = self.debug
            print(self.instrument)
            # Connection test
            val = self.__read_register(DPSRegister.MODEL, 0)
            print (val)
            # Set power off if connection test succeeds
            self.set_power(False)
        except (SerialException, ModbusException, NoResponseError) as error:
            print(error)
            return False, 'Serial exception'

        return True, str('')

    # Getters and setters
    def set_power(self, enable: bool) -> tuple[bool, str]:
        """Set current power ON/OFF status"""
        self.__write_register(DPSRegister.PWR_ONOFF, int(enable), 0)
        return True, ''

    def get_power_status(self) -> tuple[bool, int]:
        """Get current power ON/OFF status"""
        return True, self.get_registers().onoff

    def toggle_power(self) -> tuple[bool, str]:
        """Toggle power ON<->OFF"""
        current_status: tuple[bool, int] = self.get_power_status()
        toggle: bool = bool(current_status[1])
        self.set_power(not toggle)
        return True, ''

    def set_volts(self, volts: float) -> tuple[bool, str]:
        """Set voltage of DPS device"""
        #TODO: Limit check
        self.__write_register(DPSRegister.VOLTS_SET, volts, 2)
        return True, ''

    def get_volts_set(self) -> tuple[bool, float]:
        """Get set value of volts out, not necessary the actual out voltage atm"""
        return True, ivoltsf(self.get_registers().u_set)

    def get_volts_out(self) -> tuple[bool, float]:
        """Get voltage output at the moment"""
        return True, ivoltsf(self.get_registers().u_out)

    def set_amps(self, amps: float) -> tuple[bool, str]:
        """Set current of DPS device"""
        #TODO: Limit check
        self.__write_register(DPSRegister.AMPS_SET, amps, 3)
        return True, ''

    def get_amps_set(self) -> tuple[bool, float]:
        """Get set value of amps out, not necessary the actual out current atm"""
        return True, iampsf(self.get_registers().i_set)

    def get_amps_out(self) -> tuple[bool, float]:
        """Get current output at the moment"""
        return True, iampsf(self.get_registers().i_out)

    def set_volts_and_amps(self, volts: float, amps: float) -> tuple[bool, str]:
        """Set voltage and amps in single write"""
        #TODO: Limit check
        values: List[int] = [int(volts*100), int(amps*1000)]
        self.__write_registers(DPSRegister.VOLTS_SET, values)
        return True, ''

    def get_power_out(self) -> tuple[bool, float]:
        """Get current power output"""
        return True, iwattsf(self.get_registers().p_out)

    def get_printable_status(self) -> tuple[bool, str]:
        """Get dump of status variables of DPS"""
        # TODO: Move to DPSStatus() __repr__ __str__?
        self.get_registers()
        ret_str = str()
        ret_str += f'U-Set:\t\t{self.registers.u_set / 100.0}\n'
        ret_str += f'I-Set:\t\t{self.registers.i_set / 1000.0}\n'
        ret_str += f'U-Out:\t\t{self.registers.u_out / 100.0}\n'
        ret_str += f'I-Out:\t\t{self.registers.i_out / 1000.0}\n'
        ret_str += f'P-Out:\t\t{self.registers.p_out / 100.0}\n'
        ret_str += f'U-In:\t\t{self.registers.u_in / 100.0}\n'
        ret_str += f'Locked:\t\t{self.registers.lock}\n'
        ret_str += f'Protected:\t{self.registers.protect}\n'
        ret_str += f'CV/CC:\t\t{self.registers.cvcc}\n'
        ret_str += f'ONOFF:\t\t{self.registers.onoff}\n'
        ret_str += f'Backlight:\t{self.registers.b_led}\n'
        ret_str += f'Model:\t\t{self.registers.model}\n'
        ret_str += f'Firmware:\t{self.registers.version / 10.0}\n'
        return True, ret_str

    def get_registers(self) -> DPSRegisters or None:
        """Get status registers from DPS device, updates self.registers to current values"""
        reg_list: List[int] = self.__read_registers(0x0, 20)
        if len(reg_list) != 20:
            return None
        reg: DPSRegisters = self.registers
        reg.u_set = reg_list[0]
        reg.i_set = reg_list[1]
        reg.u_out = reg_list[2]
        reg.i_out = reg_list[3]
        reg.p_out = reg_list[4]
        reg.u_in = reg_list[5]
        reg.lock = reg_list[6]
        reg.protect = reg_list[7]
        reg.cvcc = reg_list[8]
        reg.model = reg_list[9]
        reg.version = reg_list[10]
        return reg

    # Private methods
    # Communication through Modbus, catch exceptions on these (TODO), used internally by class
    def __write_register(self, address: int, value: Union[int,float], num_decimals: int) -> None:
        """Write single register at address"""
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
