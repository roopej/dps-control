"""User Interfaces for DPS Control"""
import sys
from queue import SimpleQueue
from dps_controller import DPSController
from dps_cli import DPSCli
from dps_gui import DPSGui
import dps_config as conf

def main():
    """Entry point to DPS Controller"""
    # Arguments
    args: str = sys.argv

    # Create event queue
    eventq: SimpleQueue = SimpleQueue()

    # Create controller
    controller = DPSController(conf.ttyPort, conf.slave, eventq)

    if len(args) > 1 and args[1] == '--cli':
        # Create view and pass controller to it and start
        ui = DPSCli(controller)
        ui.start()
    else:
        ui = DPSGui(controller)

if __name__ == "__main__":
    main()
