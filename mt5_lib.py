import MetaTrader5 as mt5
import pandas as pd

def connect_to_mt5():
    if not mt5.initialize():
        print("initialize() failed")
        mt5.shutdown()
        return

    print("initialize() success")

def disconnect_from_mt5():
    mt5.shutdown() 
    print("shutdown() success")
    return

def get_data(symbol, timeframe, n=200):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_candlesticks(symbol, timeframe, n=200):
    return mt5.copy_rates_from_pos(symbol, timeframe, 0, n)

def get_symbols():
    return mt5.symbols_get()