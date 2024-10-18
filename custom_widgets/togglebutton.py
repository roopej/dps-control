from PySide6.QtWidgets import QPushButton

class ToggleButton(QPushButton):
    def __init__(self, *args, **kwargs) -> None:
        super(ToggleButton, self).__init__(*args, **kwargs)
        style = (
                "QPushButton:checked {"
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #009900, stop: 1 #00bb00);"
                "border-radius: 7;"
                "}"
                "QPushButton {"
                "background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #550000, stop: 1 #990000);"
                "border-radius: 7;"
                "}"
                )
        self.setStyleSheet(style)