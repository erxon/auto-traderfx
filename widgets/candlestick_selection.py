
from PyQt5.QtWidgets import QComboBox

class CandlestickSelection(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["100", "1000", "2000", "5000", "10000"])