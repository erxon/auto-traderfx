import MetaTrader5 as mt5
import pandas as pd
import time
import ta  # for technical indicators

# --- Configuration ---
SYMBOL = "EURUSD"
TIMEFRAME = mt5.TIMEFRAME_M1
RSI_PERIOD = 14
MA_PERIOD = 50
LOT_SIZE = 0.1
STOP_LOSS = 100  # in points
TAKE_PROFIT = 200
MAGIC_NUMBER = 12345

# --- Initialize connection ---
if not mt5.initialize():
    print("MT5 initialization failed")
    quit()

print("Connected to MT5 successfully")

# --- Helper functions ---
def get_data(symbol, timeframe, n=200):
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, n)
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], RSI_PERIOD).rsi()
    df['ma'] = ta.trend.SMAIndicator(df['close'], MA_PERIOD).sma_indicator()
    return df

def check_signals(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    buy_signal = prev['rsi'] < 30 and last['rsi'] > 30 and last['close'] > last['ma']
    sell_signal = prev['rsi'] > 70 and last['rsi'] < 70 and last['close'] < last['ma']

    return buy_signal, sell_signal

def get_positions(symbol):
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return []
    return positions

def close_positions(symbol):
    positions = get_positions(symbol)
    for pos in positions:
        order_type = mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).bid if order_type == mt5.ORDER_TYPE_BUY else mt5.symbol_info_tick(symbol).ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": pos.volume,
            "type": order_type,
            "position": pos.ticket,
            "price": price,
            "deviation": 20,
            "magic": MAGIC_NUMBER,
            "comment": "Close opposite",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }
        mt5.order_send(close_request)

def send_order(symbol, order_type):
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid

    sl = price - STOP_LOSS * mt5.symbol_info(symbol).point if order_type == mt5.ORDER_TYPE_BUY else price + STOP_LOSS * mt5.symbol_info(symbol).point
    tp = price + TAKE_PROFIT * mt5.symbol_info(symbol).point if order_type == mt5.ORDER_TYPE_BUY else price - TAKE_PROFIT * mt5.symbol_info(symbol).point

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": LOT_SIZE,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": MAGIC_NUMBER,
        "comment": "RSI+MA EA",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    print("Trade Result:", result)

# --- Main loop ---
counter = 0
while True:
    counter += 1
    print("running...", counter)
    
    df = get_data(SYMBOL, TIMEFRAME)
    df = get_indicators(df)

    buy_signal, sell_signal = check_signals(df)
    open_positions = get_positions(SYMBOL)

    if buy_signal and not any(p.type == mt5.POSITION_TYPE_BUY for p in open_positions):
        print("BUY")
        close_positions(SYMBOL)
        send_order(SYMBOL, mt5.ORDER_TYPE_BUY)

    elif sell_signal and not any(p.type == mt5.POSITION_TYPE_SELL for p in open_positions):
        print("SELL")
        close_positions(SYMBOL)
        send_order(SYMBOL, mt5.ORDER_TYPE_SELL)
    
    else:
        print("No signal")

    time.sleep(5)  # check once per minute
