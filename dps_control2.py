import queue
import concurrent.futures
import dps_config2 as conf
from dps_engine import DPSEngine 

# DPS command and event queues
dps_commands = queue.SimpleQueue()
dps_events = queue.SimpleQueue()


def dps_parser(name, cmd_queue, event_queue):
    '''Parser for commands from command line, interacts with DPS Engine to actually do stuff'''
    running = True
    dps = DPSEngine()
    while running:
        next_cmd = cmd_queue.get(block=True, timeout=None)
        print(f'Received command: {next_cmd}')
        if next_cmd == 'v':
            dps.set_volts(1)
            event_queue.put_nowait('e')
        if next_cmd == 'q':
            print('DPS Engine quitting...')
            event_queue.put_nowait('q')
            running = False


def event_monitor(name, event_queue):
    running = True
    while running:
        next_event = event_queue.get(block=True, timeout=None)
        print('Received event: %s' % (next_event))
        if next_event == 'q':
            print('Event monitor quitting...')
            running = False

def command_prompt(name, cmd_queue):
    running = True
    while running:
        cmd = input('DPS>' )
        cmd_queue.put_nowait(cmd)
        if cmd == 'q':
            running = False


if __name__ == '__main__':

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(dps_engine, 'DPS_Engine', dps_commands, dps_events)
        executor.submit(event_monitor, 'Event_Monitor', dps_events)
        executor.submit(command_prompt, 'Command_Prompt', dps_commands)
    # dps = threading.Thread(target=dps_engine, args=(1,dps_commands, dps_events))
    # dps.start()
    # eventmon = threading.Thread(target=event_monitor, args=(1, dps_events))
    # eventmon.start()

    # running = True
    # while running:
    #     cmd = input('DPS> ')e
    #     dps_commands.put_nowait(cmd)
    #     if cmd == 'q':
    #         running = False

    # dps.join()
    # eventmon.join()