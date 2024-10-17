from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from utils import get_button, get_label, get_lineedit

class _Bar(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(30,120)

    def paintEvent(self, e):
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width(), painter.device().height())
        painter.fillRect(rect, brush)

        # Get current state.
        dial = self.parent()._dial
        vmin, vmax = dial.minimum(), dial.maximum()
        value = dial.value()

        pen = painter.pen()
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)

        font = painter.font()
        font.setFamily('Times')
        font.setPointSize(18)
        painter.setFont(font)

        painter.drawText(25, 25, "{}-->{}<--{}".format(vmin, value, vmax))
        painter.end()

class DialBar(QtWidgets.QWidget):
    """Combination of dial and vertical bar for settings values"""
    def __init__(self, unit: str, *args, **kwargs) -> None:
        super(DialBar, self).__init__(*args, **kwargs)

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        self._bar = _Bar()
        self._dial = QtWidgets.QDial()
        self._dial.setNotchesVisible(False)
        self._dial.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Display part
        bottom_layout = QtWidgets.QHBoxLayout()
        self.volt_input: QtWidgets.QLineEdit = get_lineedit('0.00', 18, 4, Qt.FocusPolicy.StrongFocus)
        self.volt_input.setMaximumWidth(100)
        volt_unit_label: QtWidgets.QLabel = get_label(unit, 22)
        bottom_layout.addWidget(self.volt_input)
        bottom_layout.addWidget(volt_unit_label)

        layout.addWidget(self._bar)
        layout.addWidget(self._dial)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def paintEvent(self, e) -> None:
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        rect = QtCore.QRect(10, 0, painter.device().width()-20, painter.device().height()-150)
        painter.fillRect(rect, brush)