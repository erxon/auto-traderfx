import sys, threading, time
import os

from PyQt5.QtWidgets import QHBoxLayout, QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from widgets import log_widget
import mt5_lib
from bots.RSI import RSI_MACD_strategy
from widgets.timeframes_selection import TimeframeSelections
from widgets.symbols_selection import SymbolsSelection
from widgets.candlestick_selection import CandlestickSelection
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Screen size
        self.setMinimumSize(QSize(800, 600))

        # Window Name
        self.setWindowTitle("RSI + MACD Expert Advisor")
        
        # Window Label
        self.label = QLabel("RSI + MACD Expert Advisor")
        self.label.setAlignment(Qt.AlignCenter)

        # Canvas
        self.trend_canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)

        # Button Widget
        self.button = QPushButton("Run")
        self.button.setCheckable(True)
        self.button.clicked.connect(self.start_stop_btn)

        # Symbol, Timeframe, Candlesticks selection
        self.symbols = SymbolsSelection()
        self.selected_symbol = "USDJPY"
        self.symbols.setCurrentText("USDJPY")
        self.symbols.activated.connect(self.on_select_symbol)
        self.timeframes = TimeframeSelections()
        self.selected_timeframe = "M30"
        self.timeframes.setCurrentText("M30")
        self.timeframes.activated.connect(self.on_select_timeframe)
        self.candlesticks = CandlestickSelection()
        self.selected_candlesticks = "1000"
        self.candlesticks.setCurrentText("1000")
        self.candlesticks.activated.connect(self.on_select_candlesticks)

        # Log Widget (ReadOnly)
        self.log_box = log_widget.LogWidget()

        # Controls
        self.first_section_label = QLabel("Controls and Logs")
        self.controls = QVBoxLayout()
        self.controls.addWidget(self.label)
        self.controls.addWidget(self.candlesticks)
        self.controls.addWidget(self.symbols)
        self.controls.addWidget(self.timeframes)
        self.controls.addWidget(self.button)
        self.controls.addWidget(self.log_box)

        # Plot Layout
        self.plot_layout = QVBoxLayout()
        self.plot_layout.addWidget(self.trend_canvas)
        self.plot_layout.addWidget(self.canvas)
        
        # Main Layout
        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls)
        self.main_layout.addLayout(self.plot_layout, 1)
        
        container = QWidget()
        container.setLayout(self.main_layout)

        self.setCentralWidget(container)

        self.running = False

    def on_select_symbol(self):
        self.selected_symbol = self.symbols.currentText()

    def on_select_timeframe(self):
        self.selected_timeframe = self.timeframes.currentText()

    def on_select_candlesticks(self):
        self.selected_candlesticks = self.candlesticks.currentText()

    def start_stop_btn(self, checked):
        if checked:
            self.button.setText("Stop")
            self.initialize_bot()
        else:  
            self.button.setText("Run")
            self.shutdown_bot()

    def initialize_bot(self):
        log_widget.LogWidget.write(self.log_box, "MT5 Started")
        self.start_up()
        self.running = True

        threading.Thread(target=self.bot_loop, daemon=True).start()
            
    def shutdown_bot(self):
        self.running = False
        self.stop_mt5()

    def start_up(self):
        start = mt5_lib.connect_to_mt5()
        dataframe = mt5_lib.get_candlesticks(self.selected_symbol, self.selected_timeframe, int(self.selected_candlesticks))
            
        if start:
            init_symbol = mt5_lib.initialize_symbol(self.selected_symbol)
            if init_symbol:
                log_widget.LogWidget.write(self.log_box, f"{self.selected_symbol} successfully initialized")
            else:
                log_widget.LogWidget.write(self.log_box, f"Something went wrong initializing {self.selected_symbol}")
        
        
    def stop_mt5(self):
        mt5_lib.disconnect_from_mt5()
        log_widget.LogWidget.write(self.log_box, "MT5 Stopped")
        self.running = False
        print("Stopped")
    
    def bot_loop(self):
        symbol = self.selected_symbol
        timeframe = self.selected_timeframe
        candlesticks = int(self.selected_candlesticks)

        log_widget.LogWidget.write(self.log_box, f"Loaded Candlesticks: {candlesticks}")
        log_widget.LogWidget.write(self.log_box, f"Bot started with symbol {symbol} and timeframe {timeframe} at {time.ctime()}")

        while self.running:

            trade_outcome = RSI_MACD_strategy.rsi_macd_strategy(symbol=symbol, timeframe=timeframe, candlesticks=candlesticks)  
            dataframe = RSI_MACD_strategy.get_data(symbol=symbol, timeframe=timeframe, candlesticks=candlesticks)
            dataframe = RSI_MACD_strategy.calc_indicators(dataframe=dataframe)

            # RSI Plot
            self.canvas.axes.clear()
            self.trend_canvas.axes.clear()
            self.trend_canvas.axes.plot(dataframe["time"], dataframe["close"], label="Close")
            self.trend_canvas.axes.plot(dataframe["time"], dataframe["SMA_200"], label="SMA_200")
            self.trend_canvas.axes.legend()
            self.trend_canvas.draw()
            self.canvas.axes.plot(dataframe["time"], dataframe["rsi"], label="RSI")
            self.canvas.axes.plot(dataframe["time"], dataframe["macd"], label="MACD")
            self.canvas.axes.legend()
            self.canvas.draw()

            log_widget.LogWidget.write(self.log_box, f"Trade outcome: {trade_outcome}")
            log_widget.LogWidget.write(self.log_box, f"Processed at {time.ctime()}")
            
            time.sleep(60)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())