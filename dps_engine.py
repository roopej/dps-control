# Engine
import time
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

class DPSEngine:
    """Class interacting with DPS5005 through Modbus protocol"""
    def __init__(self, port=conf.port, slave=conf.slave):
        """Constructor"""
        self.port = port
        self.instrument = None
        self.slave = slave
        self.debug = conf.debug
    def connect(self):
        """Connect to DPS through modbus"""
        self.instrument = minimalmodbus.Instrument(port=self.port, slaveaddress=self.slave)
        self.instrument.serial.baudrate = 9600
        self.instrument.serial.bytesize = 8
        self.instrument.serial.timeout = 0.5
        self.instrument.mode = minimalmodbus.MODE_RTU
        self.instrument.close_port_after_each_call = False
        self.instrument.debug = self.debug
        print('Connect to DPS')

    # Getters and setters
    def set_power(self, enable):
        """Switch power output ON/OFF"""
        self.write_register(DPSRegister.PWR_ONOFF, enable, 0)

    def get_power(self):
        """Get current power ON/OFF status"""
        power = self.read_register(DPSRegister.PWR_ONOFF, 0)
        return power

    def toggle_power(self):
        """Toggle power ON<->OFF"""
        current_status = self.get_power()
        self.set_power(not current_status)

    def set_volts(self, volts):
        """Set voltage of DPS device"""
        #TODO: Limit check
        self.write_register(DPSRegister.VOLTS_SET, volts, 2)

    def get_volts_set(self):
        """Get set value of volts out, not necessary the actual out voltage atm"""
        volts = self.read_register(DPSRegister.VOLTS_SET, 2)
        return volts

    def get_volts_out(self):
        """Get voltage output at the moment"""
        volts = self.read_register(DPSRegister.VOLTS_OUT, 2)
        return volts

    def set_amps(self, amps):
        """Set current of DPS device"""
        #TODO: Limit check
        self.write_register(DPSRegister.AMPS_SET, amps, 3)

    def get_amps_set(self):
        """Get set value of amps out, not necessary the actual out current atm"""
        volts = self.read_register(DPSRegister.AMPS_SET, 3)
        return volts

    def get_amps_out(self):
        """Get current output at the moment"""
        volts = self.read_register(DPSRegister.AMPS_OUT, 3)
        return volts

    def get_power_out(self):
        """Get current power output"""
        power = self.read_register(DPSRegister.PWR_OUT, 2)
        return power

    def get_status(self):
        """Get dump of status variables of DPS, 20 registers starting from 0x0"""
        b = self.read_registers(0x0, 20)
        return b

    # Communication through Modbus
    def write_register(self, address, value, num_decimals):
        """Write single register at at address"""
        self.instrument.write_register(address, value=value, number_of_decimals=num_decimals)
        print('Write register')
    def read_register(self, address, num_decimals):
        """Read single register from address"""
        retval = self.instrument.read_register(address, num_decimals)
        return retval
    def read_registers(self, address, number):
        """Read number of registers starting from address"""
        registers = self.instrument.read_registers(registeraddress=address, number_of_registers=number)
        return registers

    # Utilities
    def get_status_string(self):
        """Get string representation of status dump"""
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