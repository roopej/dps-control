from dataclasses import dataclass, field
"""
DPSStatus module represents the status of the controller, including the registers of DPS device
"""

@dataclass
class DPSRegisters:
    """Values of DPS registers"""
    u_set: int = 0
    i_set: int = 0
    u_out: int = 0
    i_out: int = 0
    p_out: int = 0
    u_in: int = 0
    lock: int = 0
    protect: int = 0
    cvcc: int = 0
    onoff: int = 0
    b_led: int = 0
    model: int = 0
    version: int = 0

@dataclass
class DPSStatus:
    """State variables of a DPS device"""
    registers: DPSRegisters = field(default_factory=DPSRegisters)
    connected: bool = False
    port: str = "/dev/ttyUSB0"
    slave: int = 1
    bauds: int = 9600
    debug: bool = True

if __name__ == "__main__":
    print("DPSStatus is a POD, not to be run")
