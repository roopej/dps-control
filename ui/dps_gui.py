"""DPS-Control GUI"""
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QFile, QTextStream, QThreadPool, Slot
from custom_widgets import dialbar, statusindicator
from custom_widgets.statusindicator import StatusIndicator
from lib.dps_controller import DPSController
from lib.dps_status import DPSStatus
from lib.utils import button_factory, get_label, get_lineedit, ivoltsf, iampsf, iwattsf
import ui.breeze_pyside6

# Names for UI objects we use
DEFAULT_FONT = 'Arial'
VOUT_NAME = 'volts_out'
AOUT_NAME = 'amps_out'
POUT_NAME = 'power_out'
VIN_NAME = 'volts_in'
CV_NAME = 'cv_indicator'
CC_NAME = 'cc_indicator'
CONN_NAME = 'conn_indicator'
SETBUTTON_NAME = 'button_set'
CLIEDIT_NAME = 'cli_edit'
PORT_NAME = 'port_edit'

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
        self.__running = False

    # Private UI setup methods
    def __get_setup_panel(self) -> QVBoxLayout:
        """This is the leftmost panel containing setup items"""
        layout = QVBoxLayout()
        fontsize = 14
        port_label: QLabel = get_label('Port', fontsize)
        port_edit: QLineEdit = get_lineedit('', fontsize)
        port_edit.setObjectName(PORT_NAME)
        port_edit.setMaximumWidth(140)
        port_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        port_edit.setText(self.controller.get_port())
        port_edit.setEnabled(False)
        baud_label: QLabel = get_label('Baud rate', fontsize)
        baud_edit: QLineEdit = get_lineedit('', fontsize, 6)
        baud_edit.setMaximumWidth(140)
        baud_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        baud_edit.setText(self.controller.get_baud_rate())
        baud_edit.setEnabled(False)
        slave_label:QLabel = get_label('Slave', fontsize)
        slave_edit: QLineEdit = get_lineedit('', fontsize, 2)
        slave_edit.setMaximumWidth(140)
        slave_edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        slave_edit.setText(self.controller.get_slave())
        slave_edit.setEnabled(False)

        cv_hbox = QHBoxLayout()
        cv_label: QLabel = get_label('CV', 12)
        cv_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        cv_indicator = statusindicator.StatusIndicator(size = 20)
        cv_indicator.setObjectName(CV_NAME)
        cv_hbox.addStretch()
        cv_hbox.addWidget(cv_label)
        cv_hbox.addWidget(cv_indicator)

        cc_hbox = QHBoxLayout()
        cc_label: QLabel = get_label('CC', 12)
        cc_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        cc_indicator = statusindicator.StatusIndicator(size = 20)
        cc_indicator.setObjectName(CC_NAME)
        cc_hbox.addStretch()
        cc_hbox.addWidget(cc_label)
        cc_hbox.addWidget(cc_indicator)

        status_hbox = QHBoxLayout()
        status_label = get_label('Connected', 12)
        status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        status_indicator = statusindicator.StatusIndicator(size = 20)
        status_indicator.setObjectName(CONN_NAME)
        status_hbox.addStretch()
        status_hbox.addWidget(status_label)
        status_hbox.addWidget(status_indicator)

        button_connect: QPushButton = button_factory('Connect')
        button_connect.setObjectName('button_connect')
        button_connect.clicked.connect(self, self.__handle_buttons)

        layout.addWidget(QHLine())
        layout.addWidget(port_label)
        layout.addWidget(port_edit)
        layout.addWidget(baud_label)
        layout.addWidget(baud_edit)
        layout.addWidget(slave_label)
        layout.addWidget(slave_edit)
        layout.addStretch()
        layout.addWidget(QHLine())
        layout.addLayout(cv_hbox)
        layout.addLayout(cc_hbox)
        layout.addLayout(status_hbox)
        layout.addWidget(button_connect)
        return layout

    def __controls_changed(self, *args) -> None:
        """Handle signal from control UI element"""
        if self.controller.status.connected:
            self.button_set.setEnabled(True)

    def __get_control_panel(self) -> QVBoxLayout:
        """Panel for setting volts and amps"""
        layout = QVBoxLayout()

        # Dials for Volts and Amps
        va_dial_layout = QHBoxLayout()
        volt_control = dialbar.DialBar('V', 4)
        volt_control.setObjectName('volt_control')
        amp_control = dialbar.DialBar('A', 5)
        amp_control.setObjectName('amp_control')
        volt_control.set_range(0.0, 3.0)
        amp_control.set_range(0,5)

        # Connect change signals
        volt_control.valuesChanged.connect(self.__controls_changed)
        amp_control.valuesChanged.connect(self.__controls_changed)

        # Add to layout
        va_dial_layout.addWidget(volt_control)
        va_dial_layout.addStretch()
        va_dial_layout.addWidget(amp_control)

        # Button to commit values
        self.button_set: QPushButton = button_factory('Set')
        self.button_set.setObjectName(SETBUTTON_NAME)
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
        volt_out_edit.setObjectName(VOUT_NAME)
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
        amp_out_edit.setObjectName(AOUT_NAME)
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
        power_out_edit.setObjectName(POUT_NAME)
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
        volt_in_edit.setObjectName(VIN_NAME)
        volt_in_unit_label: QLabel = get_label('V', label_size)
        volt_in_unit_label.setMargin(7)
        volt_in_hbox.addWidget(volt_in_edit)
        volt_in_hbox.addWidget(volt_in_unit_label)

        self.button_onoff = button_factory('Power', toggle=True)
        self.button_onoff.setCheckable(True)
        self.button_onoff.setObjectName('button_onoff')
        self.button_onoff.setEnabled(False)

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
        cli_input.setObjectName(CLIEDIT_NAME)
        cli_input.setEnabled(True)
        cli_input.editingFinished.connect(self.__handle_cli_command)
        layout.addWidget(cliLabel)
        layout.addWidget(cli_input)
        return layout

    def closeEvent(self, event):
        self.controller.event_queue.put_nowait(None)
        self.__running = False

    # Private functional methods
    def __handle_cli_command(self) -> None:
        """Get input from CLI edit box and send it as command to the controller"""
        cli_edit = self.findChild(QLineEdit, CLIEDIT_NAME)
        command = cli_edit.text()
        if len(command):
            print(command)
            ret, msg = self.controller.parse_command(command)
            self.log(msg)
            if command == 'q':
                self.close()
            cli_edit.setText('')
            self.__update_status(self.controller.status)


    def __handle_buttons(self) -> None:
        """Handle button presses from UI, form command for controller"""
        cmd: str
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
            #  * Check that power is actually on
            #  * Set toggle button status accordingly
        elif sender_name == 'button_connect':
            self.log('Connecting')
            cmd: str = f'c {self.controller.status.port}'

            ret, msg = self.controller.parse_command(cmd)
            # We are connected, light LED
            if ret:
                connected_ind = self.findChild(StatusIndicator, CONN_NAME)
                connected_ind.setEnabled(True)
                button_set = self.findChild(QPushButton, SETBUTTON_NAME)
                button_set.setEnabled(True)
                cli_edit = self.findChild(QLineEdit, CLIEDIT_NAME)
                cli_edit.setEnabled(True)
            else:
                self.log(msg)

            # TODO:
            #  * Check if connection was successful
            #  * Set connected LED accordingly
            #  * No disconnect option necessary
        elif sender_name == 'button_set':
            vcontrol = self.findChild(dialbar.DialBar, name = 'volt_control')
            acontrol = self.findChild(dialbar.DialBar, name = 'amp_control')
            vstr = vcontrol.get_value()
            astr = acontrol.get_value()
            cmd: str = f'va {vstr} {astr}'
            self.log(f'Set output: {vstr} V {astr} A')
            # TODO:
            #  * Check minimum and maximum limits and cancel if necessary
            sender.setEnabled(False)
        # Send command
        # self.controller.parse_command(cmd)

    def __update_status(self, status: DPSStatus):
        """Update UI according to status information"""
        vout = self.findChild(QLineEdit, VOUT_NAME)
        aout = self.findChild(QLineEdit, AOUT_NAME)
        pout = self.findChild(QLineEdit, POUT_NAME)
        vin = self.findChild(QLineEdit, VIN_NAME)
        cv = self.findChild(StatusIndicator, CV_NAME)
        cc = self.findChild(StatusIndicator, CC_NAME)
        vout.setText(str(ivoltsf(status.registers.u_out)))
        aout.setText(str(iampsf(status.registers.i_out)))
        pout.setText(str(iwattsf(status.registers.p_out)))
        vin.setText(str(ivoltsf(status.registers.u_in)))
        port_edit = self.findChild(QLineEdit, PORT_NAME)
        port_edit.setText(self.controller.status.port)

        # Handle CV/CC indicator
        if self.controller.status.connected:
            if status.registers.cvcc == 0:
                cv.setEnabled(True)
                cc.setEnabled(False)
            else:
                cv.setEnabled(False)
                cc.setEnabled(True)

        self.update()




    @Slot()
    def __handle_events(self):
        """Handle event from controller, render status into GUI components"""
        while self.__running:
            print('Waiting for event to appear...')
            data = self.controller.event_queue.get()
            if data is None:
                print('Event handler quitting...')
                break
            print(data)
            self.__update_status(data)


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

        # Set up event handling from controller
        print('Starting event thread')
        self.thread_manager = QThreadPool()
        self.__running = True
        self.thread_manager.start(self.__handle_events)

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

def DPSGui(controller: DPSController) -> None:
    app = QApplication(sys.argv)
    set_styles(app)
    window = DPSMainWindow(controller)
    window.setup()
    window.setFixedSize(600, 750)
    window.show()
    window.log(f'dps-control v{controller.get_version()}')
    app.exec()

if __name__ == '__main__':
    DPSGui()
