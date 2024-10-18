class DPSCli:
    """CLI view, passes commands to DPS Controller"""
    def __init__(self, controller):
        """Set up all variables"""
        self.controller = controller
        self.running = False

    def command_prompt(self):
        """Get input from user and return command"""
        command = input('DPS> ')
        return command

    def command_loop(self):
        """Loop command prompt until cancelled"""
        while self.running:
            cmd = self.command_prompt()
            print(f'Command given is: {cmd}')
            self.running = self.controller.parse_command(cmd)

    def start(self):
        """Start CLI"""
        self.running = True
        portinfo = self.controller.get_portinfo()
        print(f'Connected:\t{portinfo['connected']}\nPort:\t\t{portinfo['port']}\nSlave:\t\t{portinfo['slave']}')
        self.command_loop()

if __name__ == "__main__":
    pass
