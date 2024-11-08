"""User Interfaces for DPS Control"""
import sys
import os
from yaml import safe_load, YAMLError
from lib.dps_controller import DPSController
from ui.dps_cli import DPSCli
from ui.dps_gui import dps_gui

def main():
    """dps-control application"""
    # Arguments
    args: list[str] = sys.argv

    # Try reading configuration
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    try:
        config_file = 'dps_control.cfg'
        path_to_config = os.path.abspath(os.path.join(bundle_dir, config_file))
        with open(path_to_config, 'r') as file:
            conf = safe_load(file)
    except YAMLError as error:
        print(f'Error parsing configuration file {error}')

    # Print config if debug
    if conf['misc']['debug']:
        print (conf)

    # Read preset configuration
    try:
        preset_file = str(conf['misc']['preset_filename'])
        path_to_presets = os.path.abspath(os.path.join(bundle_dir, preset_file))
        with open(path_to_presets, 'r+') as file:
            presets = safe_load(file)
    except YAMLError as error:
        print(f'Error parsing presets file {error}')

    # Create controller
    controller = DPSController(conf, presets)

    # Start CLI if requested
    if len(args) > 1 and args[1] == '--cli':
        ui = DPSCli(controller)
        ui.start()
    else:
        dps_gui(controller)

if __name__ == "__main__":
    main()
