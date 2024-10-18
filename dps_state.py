"""
DPSState module represents the registers of DPS device as well as some Modbus
related variables
"""

class DPSState:
    """State variables of a DPS device"""

    def __init__(self) -> None:
        """Constructor"""
        self.connected: bool = False
        self.port: str = "/dev/ttyUSB0"
        self.slave: int = 1
        self.volts_set: float = 0.0
        self.amps_set: float = 0.0
        self.volts_out: float = 0.0
        self.volts_in: float = 0.0
        self.amps_out: float = 0.0
        self.power_out: float = 0.0
        self.max_volts: float = 0.0
        self.max_amps: float = 0.0
        self.locked: bool = False
        self.protected: bool = False
        self.cvcc: str = "CV"
        self.onoff: bool = False
        self.backlight: int = 4
        self.model: str = ""
        self.firmware: str = ""
        self.debug: bool = True

    def __repr__(self) -> str:
        """Representation of class"""
        st = {
            "Connected": self.connected,
            "Port": self.port,
            "Slave": self.slave,
            "U-Set": self.volts_set,
            "I-Set": self.amps_set,
            "U-Out": self.volts_out,
            "I-Out": self.amps_out,
            "P-Out": self.power_out,
            "U-In": self.volts_in,
            "Locked": self.locked,
            "Protected": self.protected,
            "CV/CC": self.cvcc,
            "ON_OFF": self.onoff,
            "Backlight": self.backlight,
            "Model": self.model,
            "Firmware": self.firmware,
            "Debug": self.debug,
        }
        ret = str()
        for key, value in st.items():
            ret += f"{key}: {st[key]}\n"
        return ret

if __name__ == "__main__":
    print("DPSState is a POD, not to be run")
