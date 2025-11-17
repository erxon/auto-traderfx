import MetaTrader5 
import mt5_lib
import indicator_lib
import pandas as pd
from bots.EMA import EMA_cross_strategy
import time


def start_up():
    start = mt5_lib.connect_to_mt5()
    symbol = "EURUSD"

    if start:
        init_symbol = mt5_lib.initialize_symbol("EURUSD")
        if init_symbol:
            print(f"{symbol} successfully initialized")
            return True
        else:
            raise Exception(f"Failed to initialize")
        
    return False
    
    

if __name__ == "__main__":
    symbols = ["EURUSD"]
    timeframe = "M15"
    candles=1000
    start_up()
    for symbol in symbols:
        candlesticks = mt5_lib.get_candlesticks(
            symbol=symbol,
            timeframe=timeframe,
            number_of_candles=candles
        )

        pd.set_option('display.max_columns', None)

        while True:
            data = EMA_cross_strategy.ema_cross_strategy(
                symbol,
                timeframe,
                ema_one=50,
                ema_two=200,
                balance=100015,
                amount_to_risk=0.01 )
        
            print(data)
            time.sleep(60)







    
    

    

