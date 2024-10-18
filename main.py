"""User Interfaces for DPS Control"""
import sys
from queue import SimpleQueue
from dps_controller import DPSController
from dps_cli import DPSCli
from dps_gui import DPSGui
import yaml

def main():
    """Entry point to DPS Controller"""
    # Arguments
    args: str = sys.argv

    # Try reading configuration
    try:
        config_file = 'dps_controller.cfg'
        with open(config_file, 'r') as file:
            conf = yaml.safe_load(file)
    except yaml.YAMLError as error:
        print(f'Error parsing configurationf file {error}')

    print (conf)

    # Create event queue
    eventq: SimpleQueue = SimpleQueue()

    # Create controller
    tty_port = conf['connection']['tty_port']
    slave_num =  conf['connection']['slave']
    baud_rate =  conf['connection']['baud_rate']
    controller = DPSController(tty_port, slave_num, baud_rate, eventq)

    if len(args) > 1 and args[1] == '--cli':
        # Create view and pass controller to it and start
        ui = DPSCli(controller)
        ui.start()
    else:
        DPSGui(controller)

if __name__ == "__main__":
    main()
