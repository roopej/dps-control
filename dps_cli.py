"""
Simple CLI to use DPS Control engine
"""

from dps_controller import DPSController

class DPSCli:
    """CLI view, passes commands to DPS Controller"""
    def __init__(self, controller):
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
            print(f'Command given is: {cmd}')
            ret: tuple[bool, str] = self.controller.parse_command(cmd)
            print(ret[1])
            if cmd == 'q':
                self.running = False

    def start(self) -> None:
        """Start CLI"""
        self.running = True
        print(self.controller.get_portinfo()[1])
        self.command_loop()

if __name__ == "__main__":
    pass
