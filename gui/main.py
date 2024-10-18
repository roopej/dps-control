
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QFont, QPalette, QColor
from enum import IntEnum

import sys

from PySide6.QtWidgets import QLabel
import breeze_pyside6

DEFAULT_FONT = 'Arial'

# Helper functions
def default_font(size: int) -> QFont:
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

class QVLine(QFrame):
    def __init__(self) -> None:
        super(QVLine, self).__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(3)
        self.setMidLineWidth(1)

class QHLine(QFrame):
    def __init__(self) -> None:
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Sunken)
        self.setLineWidth(3)
        self.setMidLineWidth(1)

class DPSMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('DPS Controller')

    def __get_setup_panel(self) -> QVBoxLayout:
        """This is the leftmost panel containing setup items"""
        layout = QVBoxLayout()
        fontsize = 14
        self.portLabel: QLabel = get_label('Port', fontsize)
        self.portEdit: QLineEdit = get_lineedit('', fontsize)
        self.portEdit.setMaximumWidth(140)
        self.baudLabel: QLabel = get_label('Baud rate', fontsize)
        self.baudEdit: QLineEdit = get_lineedit('', fontsize, 6)
        self.baudEdit.setMaximumWidth(140)
        self.slaveLabel:QLabel = get_label('Slave', fontsize)
        self.slaveEdit: QLineEdit = get_lineedit('', fontsize, 2)
        self.slaveEdit.setMaximumWidth(140)
        self.connectButton = QPushButton('Connect')
        self.connectButton.setFont('Arial')

        layout.addWidget(QHLine())
        layout.addWidget(self.portLabel)
        layout.addWidget(self.portEdit)
        layout.addWidget(self.baudLabel)
        layout.addWidget(self.baudEdit)
        layout.addWidget(self.slaveLabel)
        layout.addWidget(self.slaveEdit)
        layout.addStretch()
        layout.addWidget(QHLine())
        layout.addWidget(self.connectButton)
        return layout

    def __get_control_panel(self) -> QVBoxLayout:
        """Panel for setting volts and amps"""
        layout = QVBoxLayout()

        # Volt section
        volt_label: QLabel = get_label('Volts', 20)
        volt_layout = QHBoxLayout()
        self.volt_dial = QDial()
        self.volt_dial.setMinimumWidth(100)
        self.volt_dial.notchesVisible = True
        self.volt_dial.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.volt_input: QLineEdit = get_lineedit('0.00', 18, 4, Qt.FocusPolicy.StrongFocus)
        self.volt_input.setMaximumWidth(100)
        volt_unit_label: QLabel = get_label('V', 22)

        volt_layout.addWidget(self.volt_dial)
        volt_layout.addWidget(self.volt_input)
        volt_layout.addWidget(volt_unit_label)

        # Amp section
        amp_label: QLabel = get_label('Amps', 20)
        amp_layout = QHBoxLayout()
        self.amp_dial = QDial()
        self.amp_dial.setMinimumWidth(100)
        self.amp_dial.notchesVisible = True
        self.amp_dial.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.amp_input: QLineEdit = get_lineedit('0.000', 18, 5, Qt.FocusPolicy.StrongFocus)
        self.amp_input.setMaximumWidth(100)
        amp_unit_label: QLabel = get_label('A', 22)

        amp_layout.addWidget(self.amp_dial)
        amp_layout.addWidget(self.amp_input)
        amp_layout.addWidget(amp_unit_label)
        self.setbutton = QPushButton('Set')
        self.setbutton.setMaximumWidth(100)

        layout.addWidget(QHLine())
        layout.addWidget(volt_label)
        layout.addLayout(volt_layout)
        layout.addWidget(amp_label)
        layout.addLayout(amp_layout)
        layout.addWidget(QHLine())
        layout.addWidget(self.setbutton)

        return layout

    def __get_output_panel(self) -> QVBoxLayout:
        """This is the rightmost vertical panel showing output values"""
        layout: QVBoxLayout = QVBoxLayout()

        # Stylesheet change for out values
        editstyle = (
            "QLineEdit"
            "{"
            "background: #333333;"
            "border : 1px solid ;"
            "border-color : yellow"
            "}"
        )

        label_size = 24
        vin_label: QLabel = get_label('V-IN', label_size)
        vin_hbox: QHBoxLayout = QHBoxLayout()
        vin_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        vin_edit.setStyleSheet(editstyle)
        vin_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        vin_edit.setMaximumWidth(100)
        vin_unit_label: QLabel = get_label('V', label_size)
        vin_unit_label.setMargin(7)
        vin_hbox.addWidget(vin_edit)
        vin_hbox.addWidget(vin_unit_label)

        vout_label: QLabel = get_label('V-OUT', label_size)
        vout_hbox: QHBoxLayout = QHBoxLayout()
        vout_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        vout_edit.setStyleSheet(editstyle)
        vout_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        vout_edit.setMaximumWidth(100)
        vout_unit_label: QLabel = get_label('V', label_size)
        vout_unit_label.setMargin(7)
        vout_hbox.addWidget(vout_edit)
        vout_hbox.addWidget(vout_unit_label)

        aout_label: QLabel = get_label('A-OUT', label_size)
        aout_hbox: QHBoxLayout = QHBoxLayout()
        aout_edit: QLineEdit = get_lineedit('0.000', label_size, 5, Qt.FocusPolicy.NoFocus)
        aout_edit.setStyleSheet(editstyle)
        aout_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        aout_edit.setMaximumWidth(100)
        aout_unit_label: QLabel = get_label('A', label_size)
        aout_unit_label.setMargin(7)
        aout_hbox.addWidget(aout_edit)
        aout_hbox.addWidget(aout_unit_label)

        pout_label: QLabel = get_label('P-OUT', label_size)
        pout_hbox: QHBoxLayout = QHBoxLayout()
        pout_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        pout_edit.setStyleSheet(editstyle)
        pout_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        pout_edit.setMaximumWidth(100)
        pout_unit_label: QLabel = get_label('W', label_size)
        pout_unit_label.setMargin(7)
        pout_hbox.addWidget(pout_edit)
        pout_hbox.addWidget(pout_unit_label)

        self.button_onoff: QPushButton = QPushButton('Power')

        # Pack stuff into layout
        layout.addWidget(QHLine())
        layout.addWidget(vin_label)
        layout.addLayout(vin_hbox)
        layout.addWidget(vout_label)
        layout.addLayout(vout_hbox)
        layout.addWidget(aout_label)
        layout.addLayout(aout_hbox)
        layout.addWidget(pout_label)
        layout.addLayout(pout_hbox)
        layout.addWidget(QHLine())
        layout.addWidget(self.button_onoff)


        return layout

    def __get_header_panel(self) -> QHBoxLayout:
        """This is header row for names of panels"""
        layout = QHBoxLayout()

        # Header row of labels
        setup_label: QLabel = get_label('SETUP', 22)
        setup_label.setMargin(10)
        control_label: QLabel = get_label('CONTROL', 22)
        control_label.setMargin(10)
        output_label: QLabel = get_label('OUTPUT', 22)
        output_label.setMargin(10)

        layout.addWidget(setup_label)
        layout.addWidget(control_label)
        layout.addWidget(output_label)

        return layout

    def __get_panel_layout(self) -> QHBoxLayout:
        """This is the main functional HBox containing controls etc"""
        layout = QHBoxLayout()

        # Vertical boxes inside HBox
        layout.addLayout(self.__get_setup_panel())
        layout.addWidget(QVLine())
        layout.addLayout(self.__get_control_panel())
        layout.addWidget(QVLine())
        layout.addLayout(self.__get_output_panel())
        return layout


    def setup(self) -> None:
        """Setup UI"""
        # Main vertical layout
        self.mainVLayout = QVBoxLayout()

        # Two horizontal boxes, one for headers, one for controls etc
        self.headerHLayout: QHBoxLayout = self.__get_header_panel()
        self.panelHLayout: QHBoxLayout = self.__get_panel_layout()
        self.mainVLayout.addLayout(self.headerHLayout)
        self.mainVLayout.addLayout(self.panelHLayout)

        # Central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainVLayout)
        self.setCentralWidget(self.centralWidget)


def set_styles(app: QApplication) -> None:
    """Set style from breeze themes"""
    file = QFile(":/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

if __name__ == '__main__':
    """Main application"""
    app = QApplication(sys.argv)
    set_styles(app)
    window = DPSMainWindow()
    window.setup()
    window.show()
    app.exec()
