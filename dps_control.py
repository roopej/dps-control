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
    if len(b) != 6:
        print('Invalid Modbus response')
        return

    ret_str = 'V: %s\tA: %s\tP: %s' % (b[0] / 100.0, b[1] / 1000.0, b[2] / 100.0)
    return ret_str


def set_voltage(volts):
    """Set voltage of DPS device"""
    if (volts > conf.max_voltage or volts < conf.min_voltage):
        print('Voltage must be between %d and %d' % (conf.min_voltage, conf.max_voltage))
        return
    INSTRUMENT.write_register(Register.VOLTS_SET, value=volts, number_of_decimals=2)

def set_current(amps):
    """Set current of DPS device"""
    if (amps > conf.max_current or amps < conf.min_current):
        print('Current must be between %d and %d' % (conf.min_current, conf.max_current))
        return
    INSTRUMENT.write_register(Register.AMPS_SET, value=amps, number_of_decimals=3)

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
    print('\tp <port>\tSet device port to <port> eg. /dev/ttyUSB0')
    print('\tl\t\tLive monitoring mode, exit with [CTRL-C]')
    print('\th\t\tPrint this text')
    print('\tq\t\tQuit program')

def suggest_help():
    print("Invalid command. Type h for help.")

def parse_command(cmd):
    """Parse input command"""
    ret = True
    try:
        main_cmd = cmd.split()[0].lower()
        if main_cmd == 'v':
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            volts = cmd.split()[1]
            if validateInput(volts, ValueType.FLOAT):
                volts = "{:.2f}".format(float(volts))
                msg = "%s %s %s" % ('Set voltage to:', volts, 'V')
                print(msg)
                set_voltage(float(volts))
        elif main_cmd == 'a':
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            amps = cmd.split()[1]
            if validateInput(amps, ValueType.FLOAT):
                amps = "{:.3f}".format(float(amps))
                msg = "%s %s %s" % ('Set current to:', amps, 'A')
                print(msg)
                set_current(float(amps))
        elif main_cmd == 'i':
            print('Getting info...')
            print(decode_modbus_status_response(read_registers(0x0, 20)))
        elif main_cmd == 'p':
            if len(cmd.split()) < 2:
                suggest_help()
                return ret
            global PORT
            PORT = cmd.split()[1]
            msg = '%s: %s' % ('Setting serial device port to', PORT)
            print(msg)
            initialize()
        elif main_cmd == 'l':
            print('Running live monitoring, press [CTRL-C] to stop...')

            try:
                index = 1
                while True:
                    print(decode_modbus_monitor_response(read_registers(0x02, 6)))
                    print('\x1b[2F')
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
        INSTRUMENT = minimalmodbus.Instrument(port=PORT, slaveaddress=conf.slave)
        INSTRUMENT.debug = DEBUG
        INSTRUMENT.serial.baudrate = 9600
        INSTRUMENT.serial.bytesize = 8
        INSTRUMENT.serial.timeout = 0.5
        INSTRUMENT.mode = minimalmodbus.MODE_RTU
        INSTRUMENT.close_port_after_each_call = False

        print(INSTRUMENT)
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
