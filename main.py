import MetaTrader5 
import mt5_lib
import indicator_lib
import pandas as pd
from bots.EMA import EMA_cross_strategy
import time
from bots.RSI import RSI_MACD_strategy

def start_up(symbol):
    start = mt5_lib.connect_to_mt5()

    if start:
        init_symbol = mt5_lib.initialize_symbol(symbol)
        if init_symbol:
            print(f"{symbol} successfully initialized")
            return True
        else:
            raise Exception(f"Failed to initialize")
        
    return False
    
    

if __name__ == "__main__":
    symbols = ["USDJPY"]
    timeframe = "M30"
    candles=1000

    for symbol in symbols:
        start_up(symbol)
        
        while True:
            trade_outcome = RSI_MACD_strategy.rsi_macd_strategy(
                symbol=symbol,
                timeframe=timeframe)
            
            print(trade_outcome)
            time.sleep(60 * 30)     







    
    

    

