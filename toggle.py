
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import sys
import math
import breeze_pyside6


class StatusIndicator(QLabel):
    def __init__(self, *args, **kwargs) -> None:
        super(StatusIndicator, self).__init__(*args, **kwargs)
        self.enabled: bool = False
        self.setFixedSize(25,25)
        self.enabledColor: QColor = QColor(0x0, 0xbb, 0x0)
        self.disabledColor: QColor = QColor(0x44, 0x44, 0x44)

    def setEnabled(self, ena: bool) -> None:
        self.enabled = ena

    def paintEvent(self, event):
        paint = QPainter(self)
        paint.setRenderHint(QPainter.Antialiasing)
        paint.setBrush(Qt.transparent)
        radx = self.width()/2
        rady = self.height()/2
        paint.setPen(Qt.black)
        center = QPoint(self.width()/2, self.height()/2)
        paint.setBrush(self.enabledColor if self.enabled else self.disabledColor)
        paint.drawEllipse(center, radx, rady)
        paint.end()


class ToggleButton(QPushButton):
    def __init__(self, *args, **kwargs) -> None:
        super(ToggleButton, self).__init__(*args, **kwargs)

        self.checked1_color: str = '009900'
        self.checked2_color: str = '009900'

        style = (
                "QPushButton:checked {"
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #009900, stop: 1 #00bb00);"
                "}"
                "QPushButton {"
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #990000, stop: 1 #bb0000);"
                "}"
                )
        self.setStyleSheet(style)

class SweepButton(QPushButton):
    def __init__(self, *args, **kwargs):
        super(SweepButton, self).__init__(*args, **kwargs)

        self.backgroundColors = (
            QColor(Qt.black),
            QColor(Qt.lightGray)
        )
        self.foregroundColors = (
            QColor(Qt.white),
            QColor(Qt.black)
        )

        font = self.font()
        font.setBold(True)
        self.setFont(font)

        self.hoverAnimation = QVariantAnimation(self)
        self.hoverAnimation.setStartValue(0.)
        self.hoverAnimation.setEndValue(1.)
        self.hoverAnimation.setEasingCurve(QEasingCurve.OutCubic)
        self.hoverAnimation.setDuration(400)
        self.hoverAnimation.valueChanged.connect(self.update)

    def enterEvent(self, event):
        super().enterEvent(event)
        self.hoverAnimation.setDirection(self.hoverAnimation.Direction.Forward)
        self.hoverAnimation.start()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.hoverAnimation.setDirection(self.hoverAnimation.Direction.Backward)
        self.hoverAnimation.start()

    def paintEvent(self, event):
            qp = QPainter(self)
            qp.setRenderHint(qp.RenderHint.Antialiasing)
            qp.save()

            radius = max(4, min(self.height(), self.width()) * .125)
            clipRect = QRectF(self.rect().adjusted(0, 0, -1, -1))
            borderPath = QPainterPath()
            borderPath.addRoundedRect(clipRect, radius, radius)
            qp.setClipPath(borderPath)

            qp.fillRect(self.rect(), self.backgroundColors[0])
            qp.setPen(self.foregroundColors[0])
            qp.drawText(self.rect(),
                Qt.AlignCenter|Qt.TextShowMnemonic, self.text())

            aniValue = self.hoverAnimation.currentValue()
            if aniValue:
                # use an arbitrary "center" for the radius, based on the widget size
                extent = min(self.height(), self.width()) * 3
                angle = math.atan(extent / self.width())
                reference = math.cos(angle) * (extent + self.width())
                x = self.width() - reference
                ratio = 1 - aniValue

                hoverPath = QPainterPath()
                hoverPath.moveTo(x, 0)
                hoverPath.lineTo(self.width() - reference * ratio, 0)
                hoverPath.lineTo(self.width(), extent)
                hoverPath.lineTo(x, extent)
                qp.setClipPath(hoverPath, Qt.IntersectClip)

                qp.fillRect(self.rect(), self.backgroundColors[1])
                qp.setPen(self.foregroundColors[1])
                qp.drawText(self.rect(), Qt.AlignCenter|Qt.TextShowMnemonic, self.text())

            qp.restore()
            qp.translate(.5, .5)
            qp.drawRoundedRect(clipRect, radius, radius)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Test window')
        # Main vertical layout
        self.mainVLayout = QVBoxLayout()

        # Toggle
        testa = ToggleButton('ToggleButton')
        testa.setCheckable(True)
        testa.setMinimumWidth(200)
        self.mainVLayout.addWidget(testa)

        # Sweep
        testb = SweepButton('SweepButton')
        testb.setMinimumWidth(200)
        self.mainVLayout.addWidget(testb)

        #Status indicator
        testc = StatusIndicator()
        #testc.setMinimumWidth(100)
        testc.enable(True)
        self.mainVLayout.addWidget(testc)

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

def launch_gui() -> None:
    app = QApplication(sys.argv)
    set_styles(app)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    print('Running')
    launch_gui()