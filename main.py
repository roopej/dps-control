"""CLI Interface for DPS Control"""

from queue import SimpleQueue
from dps_controller import DPSController
from dps_cli import DPSCli

def main():
    """Entry point to DPS Controller"""

    # Create event queue
    eventq: SimpleQueue = SimpleQueue()

    # Create controller
    controller = DPSController(eventq)

    # Create view and pass controller to it and start
    cli = DPSCli(controller)
    cli.start()

if __name__ == "__main__":
    main()
