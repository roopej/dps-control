# dps-control
## Simple CLI for controlling DPS5005

A very simple and brutishly wrote CLI for controlling DPS5005 power supply unit.

## Configuration

Please check first `dps_config.py` file. It has very few settings but they are important as you need to tell the CLI in which tty port your DPS5005 device is. In Ubuntu it is usually `/dev/ttyUSB0`or `/dev/ttyUSB1`. If you do not know which port your device is in, you can plug it in and check `sudo dmesg` log which shows you where it mounted the device.

Also, please set the maximum voltage and current according to your power supply specs.

If you get permission errors about your tty port it might be that your user needs to be added to the `dialout` group.

`sudo usermod -aG dialout $(whoami)`

## Running

You can run the CLI in virtual python environment with script `./setup.sh`

This will create `virtualenv` folder, install requirements there run the CLI program.

## Usage

Type `h` to get help, while there are very few commands available. You can control the voltage and current of the device by running commands:

`v 2.32` This will set the output voltage to 2.32 Volts

`a 4.23` This will set the output current to 4.23 Amps

On startup the output is switched off for safety reasons (unless you configure it on in settings). You can toggle power output ON and OFF by `x` command.
If you want to start live monitoring, you can use `l` command which shows you identical readings as you have on your DPS5005 device screen.

