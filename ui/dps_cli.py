"""
Simple CLI to use DPS Control engine
"""
from lib.dps_controller import DPSController
from lib.dps_status import DPSStatus


class DPSCli:
    """CLI view, passes commands to DPS Controller"""
    def __init__(self, controller) -> None:
        """Set up all variables"""
        self.controller: DPSController = controller
        self.running: bool = False

    def print_help(self) -> None:
        """Print generic help for commands available"""
        print(f'dps-control v{self.controller.get_version()}')
        print('-----------------------------------------------------------')
        print('Available commands:')
        print('\ta <value>\tSet current to value (float)')
        print('\tv <value>\tSet voltage to value (float)')
        print('\tx\t\tToggle output power ON/OFF. Set to OFF on startup for safety reasons.')
        print('\tp <port>\tSet device port to <port> eg. /dev/ttyUSB0')
        print('\tl\t\tLive monitoring mode, exit with [CTRL-C]')
        print('\th\t\tPrint this text')
        print('\tq\t\tQuit program')

    @staticmethod
    def command_prompt() -> str:
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
            elif cmd == 'h':
                self.print_help()
                continue
            elif cmd == 'l':
                if not self.controller.status.connected:
                    print('You are not connected to the DPS device.')
                    continue

                print('Running live monitoring, press [CTRL-C] to stop...')
                self.controller.start_events()
                try:
                    while True:
                        stat: DPSStatus = self.controller.event_queue.get(block = True, timeout= None)
                        uout =  float(stat.registers.u_out/100.0)
                        iout = float(stat.registers.i_out/1000.0)
                        pout = float(stat.registers.p_out/100.0)
                        print(f'U-Out: \x1b[1;31m{uout:.2f}\x1b[0m V\tI-Out: \x1b[1;31m{iout:.3f}\x1b[0m A\tP-Out: \x1b[1;31m{pout:.2f}\x1b[0m W')
                        print('\x1b[2F')
                except KeyboardInterrupt:
                    self.controller.stop_events()
                    print('\n')

            ret: tuple[bool, str] = self.controller.parse_command(cmd)
            print(ret[1])


    def start(self) -> None:
        """Start CLI"""
        self.running = True
        print(f'dps-control v{self.controller.get_version()}\n')
        print(self.controller.get_portinfo()[1])
        self.command_loop()

if __name__ == "__main__":
    pass
