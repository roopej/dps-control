#!/usr/bin/env python

import minimalmodbus
from enum import Enum
from serial import SerialException
from minimalmodbus import ModbusException
import dps_config as conf

# General parameters
# ttyDevice='/dev/ttyUSB0'
# ttyDevice='/dev/ttyS0'
# volts_address = 0x0
# amps_address = 0x1
# max_voltage = 50
# min_voltage = 0
# max_current = 5
# min_current = 0


volts_address = 0x0
amps_address = 0x1

# Set Modbus parameters
minimalmodbus.MODE_RTU = 'rtu'
minimalmodbus.BAUDRATE = 19200
minimalmodbus.TIMEOUT = 0.5
minimalmodbus.CLOSE_PORT_AFTER_EACH_CALL = False
instrument = None
DEBUG = True

class ValueType(Enum):
    INT = 1
    FLOAT = 2

class Register(Enum):
    VOLTS = 0x0
    AMPS = 0x1

# Decode modbus status response
def decode_modbus_status_response(b):
    if (len(b) != 20):
        print("Invalid Modbus response")
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

    if (volts > conf.max_voltage or volts < conf.min_voltage):
        print("Voltage must be between %d and %d" % (conf.min_voltage, conf.max_voltage))
        return
    try:
        instrument.write_register(Register.VOLTS, value=volts, numberOfDecimals=2)
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)

# Set device voltage
def set_current(amps):
    if (amps > conf.max_current or amps < conf.min_current):
        print("Current must be between %d and %d" % (conf.min_current, conf.max_current))
        return
    try:
        instrument.write_register(Register.AMPS, value=amps, numberOfDecimals=3)
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)

# Read registers
def read_registers():
    try:
        registers = instrument.read_registers(registeraddress=0x0, number_of_registers=20)
        return registers
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)
    return []

# Print command prompt and return input
def commandPrompt():
    cmd = input('DPS: ')
    return cmd

# Check that value can be converted to number of certain type
def validateInput(val, valtype):
    ret = True
    try:
        if (valtype == ValueType.FLOAT):
            val = float(val)
        elif (valtype == ValueType.INT):
            val = int(val)
    except ValueError:
        print("Invalid value")
        ret = False;
    return ret

# Parse command and execute it
def parseCommand(cmd):
    ret = True
    mainCmd = cmd.split()[0].lower()
    if (mainCmd == 'v'):
        volts = cmd.split()[1]
        if (validateInput(volts, ValueType.FLOAT)):
            volts = "{:.2f}".format(float(volts))
            msg = "%s %s %s" % ('Set voltage to:', volts, 'V')
            print(msg)
            set_voltage(float(volts))
    elif (mainCmd == 'a'):
        amps = cmd.split()[1]
        if (validateInput(amps, ValueType.FLOAT)):
            amps = "{:.3f}".format(float(amps))
            msg = "%s %s %s" % ('Set current to:', amps, 'A')
            print(msg)
            set_current(float(amps))
    elif (mainCmd == 'i'):
            print("Getting info...")
            print(decode_modbus_status_response(read_registers()))

    elif (mainCmd == 'q'):
        ret = False
    return ret


def initialize():
    # Initialize Modbus
    print("Initializing...")
    global instrument
    try:
        instrument = minimalmodbus.Instrument(port=conf.ttyDevice, slaveaddress=conf.slave)
        instrument.debug = DEBUG
    except (TypeError, ValueError, ModbusException, SerialException) as error:
        print(error)
        return False

    return True

# Main program
def main():
    running = True

    if (initialize() != True):
        print("ERROR: Cannot initialize Modbus")
        return

    # Main loop
    while running:
        cmd = commandPrompt()
        running = parseCommand(cmd)

if __name__ == "__main__":
    main()