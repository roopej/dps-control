"""DPS-Control GUI"""
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QFile, QTextStream
from PySide6.QtGui import QFont, QPalette, QColor
import sys
import breeze_pyside6
from custom_widgets import dialbar, statusindicator
from dps_controller import DPSController
import dps_config as conf
from utils import get_button, get_label, get_lineedit

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
        self.portLabel: QLabel = get_label('Port', fontsize)
        self.portEdit: QLineEdit = get_lineedit('', fontsize)
        self.portEdit.setMaximumWidth(140)
        self.portEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.portEdit.setText(conf.ttyPort)
        self.baudLabel: QLabel = get_label('Baud rate', fontsize)
        self.baudEdit: QLineEdit = get_lineedit('', fontsize, 6)
        self.baudEdit.setMaximumWidth(140)
        self.baudEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.baudEdit.setText('9600')
        self.slaveLabel:QLabel = get_label('Slave', fontsize)
        self.slaveEdit: QLineEdit = get_lineedit('', fontsize, 2)
        self.slaveEdit.setMaximumWidth(140)
        self.slaveEdit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.slaveEdit.setText(str(conf.slave))

        statusHBox = QHBoxLayout()
        status_line = get_label('Connected', 12)
        status_line.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        status_indicator = statusindicator.StatusIndicator(size = 20)
        statusHBox.addStretch()
        statusHBox.addWidget(status_line)
        statusHBox.addWidget(status_indicator)

        self.button_connect: QPushButton = get_button('Connect')
        self.button_connect.setObjectName('button_connect')
        self.button_connect.clicked.connect(self, self.__handle_buttons)

        layout.addWidget(QHLine())
        layout.addWidget(self.portLabel)
        layout.addWidget(self.portEdit)
        layout.addWidget(self.baudLabel)
        layout.addWidget(self.baudEdit)
        layout.addWidget(self.slaveLabel)
        layout.addWidget(self.slaveEdit)
        layout.addStretch()
        layout.addWidget(QHLine())
        layout.addLayout(statusHBox)
        layout.addWidget(self.button_connect)
        return layout

    def __get_control_panel(self) -> QVBoxLayout:
        """Panel for setting volts and amps"""
        layout = QVBoxLayout()

        # Dials for Volts and Amps
        va_dial_layout = QHBoxLayout()
        vcontrol = dialbar.DialBar('V', 4)
        acontrol = dialbar.DialBar('A', 5)
        vcontrol.set_range(0.0, 3.0)
        acontrol.set_range(0,5)
        va_dial_layout.addWidget(vcontrol)
        va_dial_layout.addStretch()
        va_dial_layout.addWidget(acontrol)

        # Button to commit values
        self.button_set: QPushButton = get_button('Set')
        self.button_set.setObjectName('button_set')
        self.button_set.setMinimumWidth(150)
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
        pout_unit_label.setMargin(3)
        pout_hbox.addWidget(pout_edit)
        pout_hbox.addWidget(pout_unit_label)

        self.button_onoff: QPushButton = get_button('Power')
        self.button_onoff.setObjectName('button_onoff')
        self.button_onoff.setEnabled(False)
        self.button_onoff.clicked.connect(self, self.__handle_buttons)

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
                set_button_bg(sender, '#00cc00')
            else:
                self.log('Switching power OFF')
                set_button_bg(sender, '', True)
            # TODO: Send command here
        elif sender_name == 'button_connect':
            pass
        elif sender_name == 'button_set':
            cmd: str = f'va {self.volt_input.text()} {self.amp_input.text()}'
            self.log(f'Set output: {self.volt_input.text()} V {self.amp_input.text()} A')
            # TODO: Send command here

    # Public methods
    def setup(self) -> None:
        """Setup UI"""
        # Main vertical layout
        self.mainVLayout = QVBoxLayout()

        # Two horizontal boxes, one for headers, one for controls etc
        self.headerHLayout: QHBoxLayout = self.__get_header_panel()
        self.panelHLayout: QHBoxLayout = self.__get_panel_layout()
        self.logHLayout: QHBoxLayout = self.__get_log_layout()
        self.cliHLayout: QHBoxLayout = self.__get_cli_layout()

        self.mainVLayout.addLayout(self.headerHLayout)
        self.mainVLayout.addLayout(self.panelHLayout)
        logLabel: QLabel = get_label('Log:', 12)
        self.mainVLayout.addWidget(logLabel)
        self.mainVLayout.addLayout(self.logHLayout)

        self.mainVLayout.addLayout(self.cliHLayout)

        # Central widget
        self.centralWidget = QWidget()
        self.centralWidget.setLayout(self.mainVLayout)
        self.setCentralWidget(self.centralWidget)

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
    window.setFixedSize(600, 700)
    window.show()
    window.log(f'dps-control v{controller.get_version()}\n')

    #print(window.palette().window().color().name())

    app.exec()

if __name__ == '__main__':
    launch_gui()
