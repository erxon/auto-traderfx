from backtesting import Strategy
from backtesting.lib import crossover
import pandas as pd
import pandas_ta as ta
import MetaTrader5 as mt
from datetime import datetime

mt.initialize()
dataframe = pd.DataFrame(mt.copy_rates_range("USDJPY", mt.TIMEFRAME_M30, datetime(2025, 1, 1), datetime(2025, 11, 21)))
dataframe["Datetime"] = dataframe["time"].apply(lambda x: datetime.fromtimestamp(x))
dataframe["Open"] = pd.to_numeric(dataframe["open"]).astype(float)
dataframe["High"] = pd.to_numeric(dataframe["high"]).astype(float)
dataframe["Low"] = pd.to_numeric(dataframe["low"]).astype(float)
dataframe["Close"] = pd.to_numeric(dataframe["close"]).astype(float)
dataframe["Volume"] = dataframe["tick_volume"]
dataframe = dataframe[["Datetime", "Open", "High", "Low", "Close", "Volume"]]

dataframe = dataframe.dropna()

class RsiMacdStrategy(Strategy):
    # RSI parameters
    rsi_period = 14
    rsi_upper = 70
    rsi_lower = 30
    
    # MACD parameters
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9

    def init(self):
        close = self.data.Close
        self.rsi = self.I(ta.rsi, pd.Series(close), 14)


    def next(self):
        if crossover(self.rsi, self.rsi_lower):
            self.position.close()
            self.sell()
        elif crossover(self.rsi, self.rsi_upper):
            self.position.close()
            self.buy()

# You would then run this with:
from backtesting import Backtest


bt = Backtest(dataframe, RsiMacdStrategy, cash=100000, commission=.002)
stats = bt.run()

with open("stats.txt", "w") as f:
    f.write(str(stats))

bt.plot()