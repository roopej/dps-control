"""User Interfaces for DPS Control"""
import sys
from queue import SimpleQueue
from yaml import safe_load, YAMLError
from lib.dps_controller import DPSController
from ui.dps_cli import DPSCli
from ui.dps_gui import DPSGui

def main():
    """dps-control application"""
    # Arguments
    args: list[str] = sys.argv

    # Try reading configuration
    try:
        config_file = 'dps_control.cfg'
        with open(config_file, 'r') as file:
            conf = safe_load(file)
    except YAMLError as error:
        print(f'Error parsing configurationf file {error}')

    # Print config if debug
    if conf['misc']['debug']:
        print (conf)

    # Create controller
    controller = DPSController(conf)

    # Start CLI if requested
    if len(args) > 1 and args[1] == '--cli':
        ui = DPSCli(controller)
        ui.start()
    else:
        DPSGui(controller)

if __name__ == "__main__":
    main()
