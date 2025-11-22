from PyQt5.QtWidgets import QComboBox

class TimeframeSelections(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"])