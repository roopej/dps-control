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
        meter_width = 35

        # Draw black meter bar, leave space for meter on right
        painter = QtGui.QPainter(self)
        brush = QtGui.QBrush()
        brush.setColor(QtGui.QColor('black'))
        brush.setStyle(Qt.SolidPattern)
        rect = QtCore.QRect(0, 0, painter.device().width()-meter_width, painter.device().height())
        painter.fillRect(rect, brush)

        # Get current state.
        dial = self.parent()._dial
        vmin, vmax = dial.minimum(), dial.maximum()
        value = dial.value()

        # Padding for bar
        padding = 5

        # Define our canvas.
        d_height = painter.device().height() - (padding * 2)
        d_width = painter.device().width() - (padding * 2)
        pc = (value - vmin) / (vmax - vmin)
        bar_height = pc * d_height

        # Meter
        num_lines: int = int(vmax / 1000)
        line_space: float = d_height / num_lines

        # Labels
        pen = painter.pen()
        pen.setColor(QtGui.QColor(235, 186, 52, 127))
        painter.setPen(pen)

        font = painter.font()
        font.setFamily('Arial')
        font.setPointSize(8)
        painter.setFont(font)

        step: int = int(num_lines / 10)
        if step == 0:
            step = 1

        #painter.drawText(25, 25, "{}-->{}<--{}".format(vmin, value, vmax))
        print(f'Height: {d_height} Width: {d_width} PC:{pc}, bar_height: {bar_height}, min: {vmin}, max: {vmax}, line_space: {line_space}')
        for n in range(0, num_lines+1, step):
            x1 = d_width - 30
            x2 = d_width - 15
            y = d_height - int(n * line_space)

            #print(f'{x1=} {y1=} {x2=} {y2=}')
            painter.drawLine(x1, y, x2, y)
            painter.drawText(x2 + 2, y+8, f'{n:.1f}')

        # Draw bar
        rect = QtCore.QRect(5, d_height-bar_height, d_width-meter_width-padding, bar_height)
        brush.setColor(QtGui.QColor('yellow'))
        painter.fillRect(rect, brush)
        painter.end()

class DialBar(QtWidgets.QWidget):
    """Combination of dial and vertical bar for settings values"""
    def __init__(self, unit: str, *args, **kwargs) -> None:
        super(DialBar, self).__init__(*args, **kwargs)

        # Instance variables
        self._max_value : float = 0.0
        self._min_value : float = 0.0

        # Main layout
        layout = QtWidgets.QVBoxLayout()
        self._bar = _Bar()
        self._dial = QtWidgets.QDial()
        self._dial.setNotchesVisible(True)
        self._dial.setNotchTarget(60)
        self._dial.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._dial.valueChanged.connect(self._value_changed)

        # Display part
        bottom_layout = QtWidgets.QHBoxLayout()
        self._input: QtWidgets.QLineEdit = get_lineedit('0.00', 18, 4, Qt.FocusPolicy.StrongFocus)
        self._input.setMaximumWidth(100)
        self._input.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        volt_unit_label: QtWidgets.QLabel = get_label(unit, 22)
        bottom_layout.addWidget(self._input)
        bottom_layout.addWidget(volt_unit_label)

        layout.addWidget(self._bar)
        layout.addWidget(self._dial)
        layout.addLayout(bottom_layout)
        self.setLayout(layout)

    def _value_changed(self):
        """Handle dial value change event"""
        self._input.setText(str(self._dial.value()/1000))
        self._bar.update()

    def set_range(self, min : float, max : float):
        """Set range of the dial"""
        self._min_value = min
        self._max_value = max
        self._dial.setMinimum(int(self._min_value*1000))
        self._dial.setMaximum(int(self._max_value*1000))

    def get_value(self) -> float:
        """Get value of input field as float"""
        try:
            val : float = float(self.input.text())
        except ValueError:
            return 0.0
        return val

    # def paintEvent(self, e) -> None:
    #     painter = QtGui.QPainter(self)
    #     brush = QtGui.QBrush()
    #     brush.setColor(QtGui.QColor('black'))
    #     brush.setStyle(Qt.BrushStyle.SolidPattern)
    #     rect = QtCore.QRect(10, 0, painter.device().width()-20, painter.device().height()-150)
    #     painter.fillRect(rect, brush)