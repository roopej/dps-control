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

# Set Modbus parameters
minimalmodbus.MODE_RTU = 'rtu'
minimalmodbus.BAUDRATE = 19200
minimalmodbus.TIMEOUT = 0.5
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = False
INSTRUMENT = None
DEBUG = True

class ValueType(IntEnum):
    """Type of a value"""
    INT = 1
    FLOAT = 2

class Register(IntEnum):
    """Register entries"""
    VOLTS = 0x0
    AMPS = 0x1

# Decode modbus status response
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

# Set device voltage
def set_voltage(volts):
    """Set voltage of DPS device"""
    if (volts > conf.max_voltage or volts < conf.min_voltage):
        print('Voltage must be between %d and %d' % (conf.min_voltage, conf.max_voltage))
        return
    INSTRUMENT.write_register(Register.VOLTS, value=volts, number_of_decimals=2)


# Set device current
def set_current(amps):
    """Set current of DPS device"""
    if (amps > conf.max_current or amps < conf.min_current):
        print('Current must be between %d and %d' % (conf.min_current, conf.max_current))
        return
    INSTRUMENT.write_register(Register.AMPS, value=amps, number_of_decimals=3)

# Read registers for status
def read_registers():
    """Read all registers of DPS device"""
    registers = INSTRUMENT.read_registers(registeraddress=0x0, number_of_registers=20)
    return registers


# Print command prompt and return input
def command_prompt():
    """Get command from prompt"""
    cmd = input('DPS: ')
    return cmd

# Check that value can be converted to number of certain type
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

# Print some help
def print_help():
    """Print generic help for commands available"""
    print('dps-control v%s' % (VERSION))
    print('-----------------------------------------------------------')
    print('Available commands:')
    print('\ta <value>\tSet current to value (float)')
    print('\tv <value>\tSet voltage to value (float)')
    print('\tl\t\tLive monitoring mode, exit with [CTRL-C]')
    print('\th\t\tPrint this text')
    print('\tq\t\tQuit program')

# Parse command and execute it
def parse_command(cmd):
    """Parse input command"""
    ret = True
    try:
        main_cmd = cmd.split()[0].lower()
        if main_cmd == 'v':
            volts = cmd.split()[1]
            if validateInput(volts, ValueType.FLOAT):
                volts = "{:.2f}".format(float(volts))
                msg = "%s %s %s" % ('Set voltage to:', volts, 'V')
                print(msg)
                set_voltage(float(volts))
        elif main_cmd == 'a':
            amps = cmd.split()[1]
            if validateInput(amps, ValueType.FLOAT):
                amps = "{:.3f}".format(float(amps))
                msg = "%s %s %s" % ('Set current to:', amps, 'A')
                print(msg)
                set_current(float(amps))
        elif main_cmd == 'i':
            print('Getting info...')
            print(decode_modbus_status_response(read_registers()))
        elif main_cmd == 'l':
            print('Running live monitoring, press [CTRL-C] to stop...')

            try:
                index = 1
                while True:
                    print('\tMonitoring... %d' % index)
                    print('\x1b[2F')
                    index=index+1
                    time.sleep(1)
            except KeyboardInterrupt:
                print('\n')
        elif main_cmd == 'h':
            print_help()
        elif main_cmd == 'q':
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
        INSTRUMENT = minimalmodbus.Instrument(port=conf.ttyDevice, slaveaddress=conf.slave)
        INSTRUMENT.debug = DEBUG
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)
        return False

    return True

# Main program
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
