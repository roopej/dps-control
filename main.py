"""CLI Interface for DPS Control"""
from dps_controller import DPSController
from dps_cli import DPSCli


def main():
    print('Starting...')
    controller = DPSController()
    cli = DPSCli(controller)
    cli.start()

if __name__ == "__main__":
    main()
