import MetaTrader5 as mt5
from datetime import datetime
import pandas as pd
from bots.RSI import RSI_MACD_strategy

def get_past_data(symbol, timeframe):
    start=datetime(2025, 8, 1)
    end=datetime(2025, 11, 1)

    past_data = mt5.copy_rates_range(
        symbol,
        timeframe,
        start,
        end
    )

    dataframe = pd.DataFrame(past_data)

    return dataframe

mt5.initialize()

symbol = "USDJPY"
timeframe = mt5.TIMEFRAME_M30
dataframe = get_past_data(symbol=symbol, timeframe=timeframe)

# Backtest
trade_outcomes = []

for index, row in dataframe.iterrows():
    backtest_data = dataframe.iloc[:index+1].copy()

    trade_outcome = RSI_MACD_strategy.rsi_macd_strategy(
        symbol=symbol,
        timeframe="M30",
        backtest_data=backtest_data
    )

    trade_outcomes.append({
        "time": row['time'],
        "trade_outcome": trade_outcome
    })

    print(f"Processed candle at index {index}, Trade outcome: {trade_outcome}")

mt5.shutdown()

