from PySide6.QtWidgets import QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from custom_widgets.togglebutton import ToggleButton

DEFAULT_FONT = 'Arial'

# Helper functions
def default_font(size: int = 18) -> QFont:
    font = QFont(DEFAULT_FONT)
    font.setPointSize(size)
    return font

def get_label(text: str, size: int) -> QLabel:
    label = QLabel(text)
    label.setFont(default_font(size))
    return label

def get_lineedit(text: str, fontsize: int, maxlen: int = 128, focus: Qt.FocusPolicy = Qt.FocusPolicy.ClickFocus) -> QLineEdit:
    edit = QLineEdit(text)
    font: QFont = default_font(fontsize)
    edit.setFont(font)
    edit.setFocusPolicy(focus)
    edit.setMaxLength(maxlen)
    return edit

def button_factory(text: str, toggle: bool = False) -> QPushButton:
    # Default style for non-toggle button
    btn_style = (
        "border-radius: 7;"
    )
    if not toggle:
        btn = QPushButton(text)
        btn.setStyleSheet(btn_style)
    else:
        btn = ToggleButton(text)

    btn.setFont(default_font())
    btn.setFixedSize(150, 80)
    return btn

def set_button_bg(btn: QPushButton, color: str, reset: bool = False) -> None:
    """Set button background color or reset to default"""
    color_to = color
    if reset:
        color_to = '#31363b'
    btn_style = (
        'border-radius: 7;'
        f'background-color: {color_to};'
    )
    btn.setStyleSheet(btn_style)

# Simple value validators
def validate_float(value: str) -> bool:
    """Check if string can be interpreted as float"""
    try:
        float(value)
        return True
    except ValueError:
        return False

def validate_int(value: str) -> bool:
    """Check if string can be interpreted as int"""
    try:
        int(value)
        return True
    except ValueError:
        return False

def ivoltsf(value: int) -> float:
    """Convert volts from int to float, scaling"""
    return value / 100.0

def iampsf(value: int) -> float:
    """Convert amps from int to float, scaling"""
    return value / 1000.0

def iwattsf(value: int) -> float:
    """Convert watts from int to float, scaling"""
    return value / 100.0
