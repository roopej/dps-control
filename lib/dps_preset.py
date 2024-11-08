from dataclasses import dataclass

@dataclass
class DPSPreset:
    """Values which are stored for a preset"""
    voltage: float
    current: float
    power: float
