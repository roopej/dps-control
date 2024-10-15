"""CLI Interface for DPS Control"""
import sys
from queue import SimpleQueue
from dps_controller import DPSController
from dps_cli import DPSCli
from dps_gui import launch_gui

def main():
    """Entry point to DPS Controller"""
    # Arguments
    args: str = sys.argv

    # Create event queue
    eventq: SimpleQueue = SimpleQueue()

    # Create controller
    controller = DPSController(eventq)

    if len(args) > 1 and args[1] == '--cli':
        # Create view and pass controller to it and start
        cli = DPSCli(controller)
        cli.start()
    else:
        launch_gui()
if __name__ == "__main__":
    main()
