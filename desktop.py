import sys, threading, time

from PyQt5.QtWidgets import QHBoxLayout, QTextEdit, QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, Qt
from widgets import log_widget, color
import mt5_lib
from bots.RSI import RSI_MACD_strategy

class MainWindow(QMainWindow):
    

    def __init__(self):
        super().__init__()
        # Screen size
        self.setFixedSize(QSize(800, 600))

        # Window Name
        self.setWindowTitle("RSI + MACD Expert Advisor")
        
        # Window Label
        self.label = QLabel("RSI + MACD Expert Advisor")
        self.label.setAlignment(Qt.AlignCenter)

        # Button Widget
        self.button = QPushButton("Run")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.start_stop_btn)

        # Log Widget (ReadOnly)
        self.log_box = log_widget.LogWidget()

        # Controls
        self.first_section_label = QLabel("Controls and Logs")
        self.controls = QVBoxLayout()
        self.controls.addWidget(self.label)
        self.controls.addWidget(self.button)
        self.controls.addWidget(self.log_box)

        # Plot
        self.plot = QVBoxLayout()
        self.plot.addWidget(color.Color("Blue"))

        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls)
        self.main_layout.addLayout(self.plot, 1)
        
        container = QWidget()
        container.setLayout(self.main_layout)

        self.setCentralWidget(container)

        self.running = False

    def start_stop_btn(self, checked):
        if checked:
            self.button.setText("Stop")
            self.initialize_bot()
        else:  
            self.button.setText("Run")
            self.shutdown_bot()
            

    def initialize_bot(self):
        log_widget.LogWidget.write(self.log_box, "MT5 Started")
        self.start_up("USDJPY")
        self.running = True
        threading.Thread(target=self.bot_loop, daemon=True).start()
            
    def shutdown_bot(self):
        self.running = False
        self.stop_mt5()

    def start_up(self, symbol):
        start = mt5_lib.connect_to_mt5()
        if start:
            init_symbol = mt5_lib.initialize_symbol(symbol)
            if init_symbol:
                log_widget.LogWidget.write(self.log_box, f"{symbol} successfully initialized")
            else:
                log_widget.LogWidget.write(self.log_box, f"Something went wrong initializing {symbol}")
        
        
    def stop_mt5(self):
        mt5_lib.disconnect_from_mt5()
        log_widget.LogWidget.write(self.log_box, "MT5 Stopped")
        self.running = False
        print("Stopped")
    
    def bot_loop(self):
        symbol = "USDJPY"
        timeframe = "M30"

        log_widget.LogWidget.write(self.log_box, f"Bot started with symbol {symbol} and timeframe {timeframe} at {time.ctime()}")
    
        while self.running:
            trade_outcome = RSI_MACD_strategy.rsi_macd_strategy(symbol=symbol, timeframe=timeframe)
        
            log_widget.LogWidget.write(self.log_box, f"Trade outcome: {trade_outcome}")
            log_widget.LogWidget.write(self.log_box, f"Processed at {time.ctime()}")
            
            time.sleep(60)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())