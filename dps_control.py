"""Simple script to control DPS5005 (and similar) power supplies"""
#!/usr/bin/env python

import time
from enum import IntEnum
from serial import SerialException
import minimalmodbus
from minimalmodbus import ModbusException

# Configuration file
import dps_config as conf

# Constants
VERSION = "0.1"

# Global Modbus handle
INSTRUMENT = None
PORT = conf.ttyDevice
PWRON = False

# In case of problems, set to True to see better debug prints
DEBUG = False

class ValueType(IntEnum):
    """Type of a value"""
    INT = 1
    FLOAT = 2

class Register(IntEnum):
    """Register entries"""
    VOLTS_SET = 0x0
    AMPS_SET = 0x1
    VOLTS_OUT = 0x2
    AMPS_OUT = 0x3
    PWR_OUT = 0x4
    VOLTS_UIN = 0x5
    PWR_ONOFF = 0x9

def decode_modbus_status_response(b):
    """Decode Modbus response and return printable structure"""
    if len(b) != 20:
        print('Invalid Modbus response')
        return

    rv = {'U-Set': b[0] / 100.0,
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

    return rv

def decode_modbus_monitor_response(b):
    """Decode Modbus response for live monitoring output"""
    if len(b) != 8:
        print('Invalid Modbus response')
        return
    v = b[0] / 100.0
    a = b[1] / 1000.0
    p = b[2] / 100.0
    vin = b[3] / 100.0
    ret_str = '\t%.2f V     %.3f A     %.2f W     %.2f Vin' % (v,a,p,vin)
    return ret_str


def set_voltage(volts):
    """Set voltage of DPS device"""
    if (volts > conf.max_voltage or volts < conf.min_voltage):
        print('Voltage must be between %d and %d' % (conf.min_voltage, conf.max_voltage))
        return
    INSTRUMENT.write_register(Register.VOLTS_SET, value=volts, number_of_decimals=2)

def get_voltage():
    """Get voltage setting"""
    volts = INSTRUMENT.read_register(Register.VOLTS_SET, number_of_decimals=2)
    return volts

def get_current():
    """Get current setting"""
    amps = INSTRUMENT.read_register(Register.AMPS_SET, number_of_decimals=3)
    return amps

def set_current(amps):
    """Set current of DPS device"""
    if (amps > conf.max_current or amps < conf.min_current):
        print('Current must be between %d and %d' % (conf.min_current, conf.max_current))
        return
    INSTRUMENT.write_register(Register.AMPS_SET, value=amps, number_of_decimals=3)

def toggle_power():
    """Toggle output power ON and OFF"""
    global PWRON
    PWRON = not PWRON
    INSTRUMENT.write_register(Register.PWR_ONOFF, value=PWRON, number_of_decimals=0)

def read_registers(address, number):
    """Read registers of DPS device from address (number bytes)"""
    registers = INSTRUMENT.read_registers(registeraddress=address, number_of_registers=number)
    return registers

def command_prompt():
    """Get command from prompt"""
    cmd = input('DPS> ')
    return cmd

def validateInput(val, valtype):
    """Check that value in correct format"""
    ret = True

    if valtype == ValueType.FLOAT:
        val = float(val)
    elif valtype == ValueType.INT:
        val = int(val)
    else:
        print('Invalid value')
        ret = False
    return ret

def print_help():
    """Print generic help for commands available"""
    print('dps-control v%s' % (VERSION))
    print('-----------------------------------------------------------')
    print('Available commands:')
    print('\ta <value>\tSet current to value (float)')
    print('\tv <value>\tSet voltage to value (float)')
    print('\tx\t\tToggle output power ON/OFF. Set to OFF on startup for safety reasons.')
    print('\tp <port>\tSet device port to <port> eg. /dev/ttyUSB0')
    print('\tl\t\tLive monitoring mode, exit with [CTRL-C]')
    print('\th\t\tPrint this text')
    print('\tq\t\tQuit program')

def suggest_help():
    print("Invalid command. Type h for help.")

def parse_main(cmd, *vals):
    """Parse the main command and its alternatives"""
    main_cmd = cmd.split()[0].lower()
    for val in vals:
        if main_cmd == val:
            return True
    return False

def parse_command(cmd):
    """Parse input command"""
    ret = True
    try:
        if parse_main(cmd, 'v', 'volts', 'volt'):
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            volts = cmd.split()[1]
            if validateInput(volts, ValueType.FLOAT):
                volts = "{:.2f}".format(float(volts))
                msg = "%s %s %s" % ('Set voltage to:', volts, 'V')
                print(msg)
                set_voltage(float(volts))
        elif parse_main(cmd, 'a', 'amps', 'amp'):
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            amps = cmd.split()[1]
            if validateInput(amps, ValueType.FLOAT):
                amps = "{:.3f}".format(float(amps))
                msg = "%s %s %s" % ('Set current to:', amps, 'A')
                print(msg)
                set_current(float(amps))
        elif parse_main(cmd, 'i', 'info'):
            print('Getting info...')
            print(decode_modbus_status_response(read_registers(0x0, 20)))
        elif parse_main(cmd, 'p', 'port'):
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            global PORT
            PORT = cmd.split()[1]
            msg = '%s: %s' % ('Setting serial device port to', PORT)
            print(msg)
            initialize()
        elif parse_main(cmd, 'l', 'live'):
            print('Running live monitoring, press [CTRL-C] to stop...')
            try:
                index = 1
                while True:
                    print(decode_modbus_monitor_response(read_registers(0x02, 8)))
                    print('\x1b[2F')
                    time.sleep(0.5)
            except KeyboardInterrupt:
                print('\n')
        elif parse_main(cmd, 'x', 'execute'):
            toggle_power()
        elif parse_main(cmd, 'h', '?', 'help'):
            print_help()
        elif parse_main(cmd, 'q', 'quit', 'exit'):
            ret = False
        return ret
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)
        return True

def initialize():
    """Initialize Modbus"""
    print('Initializing...')
    global INSTRUMENT
    try:
        INSTRUMENT = minimalmodbus.Instrument(port=PORT, slaveaddress=conf.slave)
        INSTRUMENT.debug = DEBUG
        INSTRUMENT.serial.baudrate = 9600
        INSTRUMENT.serial.bytesize = 8
        INSTRUMENT.serial.timeout = 0.5
        INSTRUMENT.mode = minimalmodbus.MODE_RTU
        INSTRUMENT.close_port_after_each_call = False

        if conf.start_power_off:
            INSTRUMENT.write_register(Register.PWR_ONOFF, value=0, number_of_decimals=0)

        print(INSTRUMENT)
        print('\n')
        a = get_current()
        v = get_voltage()
        print('Please note:')
        print('Initial settings: \x1b[1;31m%.2f V, %.3f A\x1b[0m' % (v, a))
        print('Output is set to these values if switched on now')
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)
        return False

    return True

def main():
    """Main program"""
    running = True

    if not initialize():
        print('ERROR: Cannot initialize Modbus')
        return

    # Main loop
    while running:
        cmd = command_prompt()
        if len(cmd):
            running = parse_command(cmd)

if __name__ == "__main__":
    main()
