import os
import sys
from pathlib import Path
from yaml import safe_load, YAMLError, dump
from dataclasses import dataclass

@dataclass
class DPSPreset:
    """Values which are stored for a preset"""
    index: int
    voltage: float
    current: float
    power: float

def read_presets(filename: str) -> list[DPSPreset]:
    """Return list of DPSPreset read from file"""
    ret: list[DPSPreset] = []
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    path_to_presets = os.path.abspath(os.path.join(bundle_dir, filename))
    with open(path_to_presets, 'r+') as file:
        presets_conf = safe_load(file)
        print(presets_conf)
        for i in range(1, 6):
            p = DPSPreset(i, presets_conf[i]['v'], presets_conf[i]['a'], presets_conf[i]['w'])
            ret.append(p)

    return ret

def write_presets(filename: str, presets: list[DPSPreset]) -> None:
    """Write list of presets into file"""
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    file_dir = Path(bundle_dir).parent.absolute()
    path_to_presets = Path(os.path.join(file_dir, filename))

    writestr = str()
    for i in range (0,5):
        writestr += f'{i+1}:\n'
        writestr += f'   v: {presets[i].voltage}\n'
        writestr += f'   a: {presets[i].current}\n'
        writestr += f'   w: {presets[i].power}\n'

    with open(path_to_presets, 'w') as file:
        file.write(writestr)

