"""
Simple CLI to use DPS Control engine
"""
from queue import SimpleQueue
from dps_controller import DPSController

class DPSCli:
    """CLI view, passes commands to DPS Controller"""
    def __init__(self, controller) -> None:
        """Set up all variables"""
        self.controller: DPSController = controller
        self.running: bool = False

    def command_prompt(self) -> str:
        """Get input from user and return command"""
        command: str = input('DPS> ')
        return command

    def command_loop(self) -> None:
        """Loop command prompt until cancelled"""
        while self.running:
            cmd: str = self.command_prompt()

            if len(cmd) == 0:
                continue

            if cmd == 'q':
                self.running = False
            elif cmd == 'l':
                print('Running live monitoring, press [CTRL-C] to stop...')
                self.controller.start_events()
                try:
                    while True:
                        event = self.controller.event_queue.get(block = True, timeout= None)
                        uout = event['U-Out']
                        iout = event['I-Out']
                        print(f'U-Out: \x1b[1;31m{uout:.2f}\x1b[0m V\tI-Out: \x1b[1;31m{iout:.3f}\x1b[0m A')
                        print('\x1b[2F')
                except KeyboardInterrupt:
                    self.controller.stop_events()
                    print('\n')

            ret: tuple[bool, str] = self.controller.parse_command(cmd)
            print(ret[1])


    def start(self) -> None:
        """Start CLI"""
        self.running = True
        print(self.controller.get_portinfo()[1])
        self.command_loop()

if __name__ == "__main__":
    pass
