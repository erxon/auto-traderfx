import MetaTrader5 as mt5
import pandas as pd
import time

# Initialize MT5 connection
if not mt5.initialize():
    print("Initialize failed:", mt5.last_error())
    quit()

symbol = "EURUSD"
timeframe = mt5.TIMEFRAME_M1   # 1-minute candles
fast_period = 9
slow_period = 21
lot = 0.1
sl_points = 100   # Stop Loss (in points)
tp_points = 200   # Take Profit (in points)

# Helper: place order
def place_order(order_type):
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        print("Symbol not found")
        return

    # Get bid/ask
    tick = mt5.symbol_info_tick(symbol)
    price = tick.ask if order_type == "buy" else tick.bid

    # Calculate SL/TP prices
    if order_type == "buy":
        sl = price - sl_points * symbol_info.point
        tp = price + tp_points * symbol_info.point
        order_type_mt5 = mt5.ORDER_TYPE_BUY
    else:
        sl = price + sl_points * symbol_info.point
        tp = price - tp_points * symbol_info.point
        order_type_mt5 = mt5.ORDER_TYPE_SELL

    # Create request
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type_mt5,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": f"SMA {order_type} signal",
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    # Send order
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print("Order failed:", result)
    else:
        print(f"✅ {order_type.upper()} ORDER EXECUTED")
        print(f"Price: {price:.5f}, SL: {sl:.5f}, TP: {tp:.5f}")
    return result

# Loop for live monitoring
while True:
    # Get latest 100 bars
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, 100)
    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")

    # Compute moving averages
    df["SMA_fast"] = df["close"].rolling(window=fast_period).mean()
    df["SMA_slow"] = df["close"].rolling(window=slow_period).mean()

    # Check crossover
    if len(df) > slow_period:
        prev_fast = df["SMA_fast"].iloc[-2]
        prev_slow = df["SMA_slow"].iloc[-2]
        curr_fast = df["SMA_fast"].iloc[-1]
        curr_slow = df["SMA_slow"].iloc[-1]

        if prev_fast < prev_slow and curr_fast > curr_slow:
            print("🟢 BUY signal")
            place_order("buy")

        elif prev_fast > prev_slow and curr_fast < curr_slow:
            print("🔴 SELL signal")
            place_order("sell")

        else:
            print("⏸ No crossover signal yet")

    # Wait for next candle
    time.sleep(60)
