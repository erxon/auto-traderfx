
from PyQt5.QtWidgets import QComboBox

class SymbolsSelection(QComboBox):
    def __init__(self):
        super().__init__()
        self.addItems(["USDJPY", "EURUSD", "GBPUSD"])