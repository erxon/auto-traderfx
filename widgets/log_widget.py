from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import Qt

class LogWidget(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

    def write(self, message):
        self.append(message)
        self.ensureCursorVisible()

    # Optional: redirect Python prints
    def flush(self):
        pass