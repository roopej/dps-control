from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QColor, QBrush
from PySide6.QtCore import QPoint

class StatusIndicator(QLabel):
    """Simple status indicator, LED-like"""
    def __init__(self, size: int, *args, **kwargs) -> None:
        super(StatusIndicator, self).__init__(*args, **kwargs)
        self.enabled: bool = False
        self.size = size
        self.setFixedSize(size,size)
        self.enabledColor: QColor = QColor(0x0, 0xbb, 0x0)
        self.disabledColor: QColor = QColor(0x44, 0x44, 0x44)

    def setEnabled(self, ena: bool) -> None:
        """Toggle between on and off states"""
        self.enabled = ena

    def paintEvent(self, event):
        """Handle paint event"""
        paint = QPainter(self)
        paint.setRenderHint(QPainter.RenderHint.Antialiasing)
        paint.setBrush(QBrush(QColor(0,0,0,255)))
        radx = self.width()/2
        rady = self.height()/2
        paint.setPen(QColor('black'))
        center = QPoint(int(self.width()/2), int(self.height()/2))
        paint.setBrush(self.enabledColor if self.enabled else self.disabledColor)
        paint.drawEllipse(center, radx, rady)
