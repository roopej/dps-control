"""DPS-Control GUI"""
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QFont, QPalette, QColor
import sys
import breeze_pyside6
from custom_widgets import dialbar, statusindicator, togglebutton
from dps_controller import DPSController
import dps_config as conf
from toggle import ToggleButton
from utils import button_factory, get_label, get_lineedit

DEFAULT_FONT = 'Arial'

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
    def __init__(self, controller: DPSController):
        super().__init__()
        self.setWindowTitle('DPS Controller')
        self.setMinimumSize(800, 600)
        self.log_pane = QPlainTextEdit()
        self.controller = controller

    # Private UI setup methods
    def __get_setup_panel(self) -> QVBoxLayout:
        """This is the leftmost panel containing setup items"""
        layout = QVBoxLayout()
        fontsize = 14
        portLabel: QLabel = get_label('Port', fontsize)
        portEdit: QLineEdit = get_lineedit('', fontsize)
        portEdit.setMaximumWidth(140)
        portEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        portEdit.setText(conf.ttyPort)
        baudLabel: QLabel = get_label('Baud rate', fontsize)
        baudEdit: QLineEdit = get_lineedit('', fontsize, 6)
        baudEdit.setMaximumWidth(140)
        baudEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        baudEdit.setText('9600')
        slaveLabel:QLabel = get_label('Slave', fontsize)
        slaveEdit: QLineEdit = get_lineedit('', fontsize, 2)
        slaveEdit.setMaximumWidth(140)
        slaveEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        slaveEdit.setText(str(conf.slave))

        statusHBox = QHBoxLayout()
        status_line = get_label('Connected', 12)
        status_line.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        status_indicator = statusindicator.StatusIndicator(size = 20)
        statusHBox.addStretch()
        statusHBox.addWidget(status_line)
        statusHBox.addWidget(status_indicator)

        self.button_connect: QPushButton = button_factory('Connect')
        self.button_connect.setObjectName('button_connect')
        self.button_connect.clicked.connect(self, self.__handle_buttons)

        layout.addWidget(QHLine())
        layout.addWidget(portLabel)
        layout.addWidget(portEdit)
        layout.addWidget(baudLabel)
        layout.addWidget(baudEdit)
        layout.addWidget(slaveLabel)
        layout.addWidget(slaveEdit)
        layout.addStretch()
        layout.addWidget(QHLine())
        layout.addLayout(statusHBox)
        layout.addWidget(self.button_connect)
        return layout

    def __controls_changed(self, *args) -> None:
        """Handle signal from control UI element"""
        self.button_set.setEnabled(True)

    def __get_control_panel(self) -> QVBoxLayout:
        """Panel for setting volts and amps"""
        layout = QVBoxLayout()

        # Dials for Volts and Amps
        va_dial_layout = QHBoxLayout()
        self.volt_control = dialbar.DialBar('V', 4)
        self.volt_control.setObjectName('volt_control')
        self.amp_control = dialbar.DialBar('A', 5)
        self.amp_control.setObjectName('amp_control')
        self.volt_control.set_range(0.0, 3.0)
        self.amp_control.set_range(0,5)

        # Connect change signals
        self.volt_control.valuesChanged.connect(self.__controls_changed)
        self.amp_control.valuesChanged.connect(self.__controls_changed)

        # Add to layout
        va_dial_layout.addWidget(self.volt_control)
        va_dial_layout.addStretch()
        va_dial_layout.addWidget(self.amp_control)

        # Button to commit values
        self.button_set: QPushButton = button_factory('Set')
        self.button_set.setObjectName('button_set')
        self.button_set.setEnabled(False)
        self.button_set.clicked.connect(self.__handle_buttons)

        # Vertical layout to return
        layout.addWidget(QHLine())
        layout.addLayout(va_dial_layout, 9)
        layout.addStretch()
        layout.addWidget(self.button_set, alignment=Qt.AlignmentFlag.AlignHCenter)

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

        label_size = 16

        volt_out_label: QLabel = get_label('Volts', label_size)
        volt_out_hbox: QHBoxLayout = QHBoxLayout()
        volt_out_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        volt_out_edit.setStyleSheet(editstyle)
        volt_out_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        volt_out_edit.setMaximumWidth(100)
        volt_out_unit_label: QLabel = get_label('V', label_size)
        volt_out_unit_label.setMargin(7)
        volt_out_hbox.addWidget(volt_out_edit)
        volt_out_hbox.addWidget(volt_out_unit_label)

        amp_out_label: QLabel = get_label('Amps', label_size)
        amp_out_hbox: QHBoxLayout = QHBoxLayout()
        amp_out_edit: QLineEdit = get_lineedit('0.000', label_size, 5, Qt.FocusPolicy.NoFocus)
        amp_out_edit.setStyleSheet(editstyle)
        amp_out_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        amp_out_edit.setMaximumWidth(100)
        amp_out_unit_label: QLabel = get_label('A', label_size)
        amp_out_unit_label.setMargin(7)
        amp_out_hbox.addWidget(amp_out_edit)
        amp_out_hbox.addWidget(amp_out_unit_label)

        power_out_label: QLabel = get_label('Power', label_size)
        power_out_hbox: QHBoxLayout = QHBoxLayout()
        power_out_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        power_out_edit.setStyleSheet(editstyle)
        power_out_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        power_out_edit.setMaximumWidth(100)
        power_out_unit_label: QLabel = get_label('W', label_size)
        power_out_unit_label.setMargin(3)
        power_out_hbox.addWidget(power_out_edit)
        power_out_hbox.addWidget(power_out_unit_label)

        volt_in_label: QLabel = get_label('V Input', label_size-4)
        volt_in_hbox: QHBoxLayout = QHBoxLayout()
        volt_in_edit: QLineEdit = get_lineedit('0.00', label_size, 4, Qt.FocusPolicy.NoFocus)
        volt_in_edit.setStyleSheet(editstyle)
        volt_in_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        volt_in_edit.setMaximumWidth(100)
        volt_in_unit_label: QLabel = get_label('V', label_size)
        volt_in_unit_label.setMargin(7)
        volt_in_hbox.addWidget(volt_in_edit)
        volt_in_hbox.addWidget(volt_in_unit_label)

        self.button_onoff = button_factory('Power', toggle=True)
        self.button_onoff.setCheckable(True)
        self.button_onoff.setObjectName('button_onoff')
        self.button_onoff.setEnabled(True)

        self.button_set.setSizePolicy(
            QSizePolicy.MinimumExpanding,
            QSizePolicy.Fixed
        )
        #self.button_set.setMinimumWidth(150)
        self.button_onoff.clicked.connect(self, self.__handle_buttons)

        # Pack stuff into layout
        layout.addWidget(QHLine())
        layout.addWidget(volt_out_label)
        layout.addLayout(volt_out_hbox)
        layout.addWidget(amp_out_label)
        layout.addLayout(amp_out_hbox)
        layout.addWidget(power_out_label)
        layout.addLayout(power_out_hbox)
        layout.addWidget(volt_in_label)
        layout.addLayout(volt_in_hbox)
        #layout.addWidget(QHLine())
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
        layout.addStretch()
        layout.addWidget(control_label)
        layout.addStretch()
        layout.addWidget(output_label)

        return layout

    def __get_panel_layout(self) -> QHBoxLayout:
        """This is the main functional HBox containing controls etc"""
        layout = QHBoxLayout()

        # Vertical boxes inside HBox
        layout.addLayout(self.__get_setup_panel())
        layout.addWidget(QVLine())
        layout.addLayout(self.__get_control_panel())
        #layout.addStretch()
        layout.addWidget(QVLine())
        layout.addLayout(self.__get_output_panel())
        return layout

    def __get_log_layout(self) -> QHBoxLayout:
        """This is the (usually) bottom part of the screen for log info"""
        layout = QHBoxLayout()
        self.log_pane.setReadOnly(True)
        self.log_pane.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.log_pane.setFont(DEFAULT_FONT)
        layout.addWidget(self.log_pane)
        return layout

    def __get_cli_layout(self) -> QHBoxLayout:
        """This is the CLI interface on very bottom"""
        layout = QHBoxLayout()

        cliLabel: QLabel = get_label('CLI:', 12)
        cli_input: QLineEdit = get_lineedit('', 14, 256, Qt.FocusPolicy.StrongFocus)
        layout.addWidget(cliLabel)
        layout.addWidget(cli_input)
        return layout

    # Private functional methods
    def __handle_buttons(self) -> None:
        """Handle button presses from UI"""
        cmd: str = str()
        self.log(cmd)
        sender = self.sender()
        sender_name = sender.objectName()
        print(sender_name)
        if sender_name == 'button_onoff':
            cmd = 'x'
            if self.controller.get_power_state() is False:
                self.log('Switching power ON')
            else:
                self.log('Switching power OFF')
            # TODO:
            #  * Warn about initial settings?
            #  * Send command here
            #  * Check that power is actually on
            #  * Set toggle button status accordingly
        elif sender_name == 'button_connect':
            self.log('Connecting')
            #cmd: str = f'c {port}'
            #self.log(f'Set output: {vstr} V {astr} A')
            # TODO:
            #  * Send command here
            #  * Check if connection was successful
            #  * Set connected LED accordingly
            #  * No disconnect option necessary
        elif sender_name == 'button_set':
            vstr = self.volt_control.get_value()
            astr = self.amp_control.get_value()
            cmd: str = f'va {vstr} {astr}'
            self.log(f'Set output: {vstr} V {astr} A')
            # TODO:
            #  * Send command here
            #  * Check minimum and maximum limits and cancel if necessary
            sender.setEnabled(False)

    # Public methods
    def setup(self) -> None:
        """Setup UI"""
        # Main vertical layout
        mainVLayout = QVBoxLayout()

        # Two horizontal boxes, one for headers, one for controls etc
        headerHLayout: QHBoxLayout = self.__get_header_panel()
        panelHLayout: QHBoxLayout = self.__get_panel_layout()
        logHLayout: QHBoxLayout = self.__get_log_layout()
        cliHLayout: QHBoxLayout = self.__get_cli_layout()

        mainVLayout.addLayout(headerHLayout, 1)
        mainVLayout.addLayout(panelHLayout, 5)
        logLabel: QLabel = get_label('Log:', 12)
        mainVLayout.addWidget(logLabel)
        mainVLayout.addLayout(logHLayout, 3)

        mainVLayout.addLayout(cliHLayout, 1)

        # Central widget
        centralWidget = QWidget()
        centralWidget.setLayout(mainVLayout)
        self.setCentralWidget(centralWidget)

    def log(self, txt: str) -> None:
        """Append log message to log panel"""
        self.log_pane.appendPlainText(txt)

def set_styles(app: QApplication) -> None:
    """Set style from breeze themes"""
    file = QFile(":/dark/stylesheet.qss")
    file.open(QFile.ReadOnly | QFile.Text)
    stream = QTextStream(file)
    app.setStyleSheet(stream.readAll())

def launch_gui(controller: DPSController) -> None:
    app = QApplication(sys.argv)
    set_styles(app)
    window = DPSMainWindow(controller)
    window.setup()
    window.setFixedSize(600, 750)
    window.show()
    window.log(f'dps-control v{controller.get_version()}')

    #print(window.palette().window().color().name())

    app.exec()

if __name__ == '__main__':
    launch_gui()
