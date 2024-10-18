from PySide6.QtWidgets import QLineEdit, QPushButton, QLabel
from PySide6.QtGui import QFont, QPalette, QColor
from PySide6.QtCore import Qt

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

def get_button(text: str) -> QPushButton:
    # Ad-hoc style
    btnStyle = (
        "border-radius: 7;"
    )
    btn = QPushButton(text)
    btn.setFont(default_font())
    btn.setStyleSheet(btnStyle)
    return btn

def set_button_bg(btn: QPushButton, color: str, reset: bool = False) -> None:
    """Set button background color or reset to default"""
    color_to = color
    if reset:
        color_to = '#31363b'
    btnStyle = (
        'border-radius: 7;'
        f'background-color: {color_to};'
    )
    btn.setStyleSheet(btnStyle)