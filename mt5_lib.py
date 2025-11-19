import MetaTrader5 as mt5
import pandas as pd

def connect_to_mt5():
    """
    Connect to MetaTrader5 by calling mt5.initialize(). This function returns True if the connection is successful, False otherwise.
    """
    try:
        mt5.initialize()
        print("initialize() success")
        return True
    except Exception as error:
        print(f"Error initializing MetaTrader5: {error}")
        return False
    
def disconnect_from_mt5():
    mt5.shutdown() 
    print("shutdown() success")
    return

def initialize_symbol(symbol):
    """
    Enable a symbol in MetaTrader5 for trading.

    :param symbol: The symbol to be enabled
    :type symbol: str
    :return: True if the symbol was successfully enabled, False otherwise
    :rtype: bool
    """
    all_symbols = mt5.symbols_get()
    symbol_names = []

    for sym in all_symbols:
        symbol_names.append(sym.name)

    if symbol in symbol_names:

        try:
            mt5.symbol_select(symbol, True)
            return True
        except Exception as error:
            print(f"Error enabling {symbol}, Error: {error}")
            return False
    
    else:
        print(f"Symbol {symbol} not in this version of MT5")
        return False

def get_candlesticks(symbol, timeframe, number_of_candles):
    
    if number_of_candles > 50000:
        return ValueError("No more than 50000 candles can be retrieved at this time")
    
    mt5_timeframe = set_query_timeframe(timeframe)
    candles = mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, number_of_candles)

    # Convert to dataframe
    dataframe = pd.DataFrame(candles)

    return dataframe

def set_query_timeframe(timeframe):
    """
    Set the timeframe for which to retrieve candlesticks.

    :param timeframe: The timeframe to be set, e.g. "M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"
    :type timeframe: str
    :return: The MetaTrader5 TIMEFRAME code for the given timeframe
    :rtype: int
    """
    
    timeframe_dict = {
        "M1": mt5.TIMEFRAME_M1,
        "M5": mt5.TIMEFRAME_M5,
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1,
        "W1": mt5.TIMEFRAME_W1,
        "MN1": mt5.TIMEFRAME_MN1
    }

    return timeframe_dict[timeframe]

def place_order(order_type, symbol, volume, stop_loss, take_profit, comment, stop_price, direct=False):
    decimal = 4

    if symbol == "USDJPY":
        decimal = 3

    volume = float(volume)
    volume = round(volume, 2)

    stop_loss = float(stop_loss)
    stop_loss = round(stop_loss, decimal)

    take_profit = float(take_profit)
    take_profit = round(take_profit, decimal)

    stop_price = float(stop_price)
    stop_price = round(stop_price, decimal)

    request = {
        "symbol": symbol,
        "volume": volume,
        "sl": stop_loss,
        "tp": take_profit,
        "type_time": mt5.ORDER_TIME_GTC,
        "comment": comment
    }

    if order_type == "SELL_STOP":
        request["type"] = mt5.ORDER_TYPE_SELL_STOP
        request["action"] = mt5.TRADE_ACTION_PENDING
        request["type_filling"] = mt5.ORDER_FILLING_RETURN
        
        if stop_price <= 0:
            raise ValueError("Stop price cannot be zero")
        else:
            request["price"] = stop_price
    elif order_type == "BUY_STOP":
        request["type"] = mt5.ORDER_TYPE_BUY_STOP
        request["action"] = mt5.TRADE_ACTION_PENDING
        request["type_filling"] = mt5.ORDER_FILLING_RETURN

        if stop_price <= 0:
            raise ValueError("Stop Price cannot be zero")
        else:
            request["price"] = stop_price
    else:
        raise ValueError(f"Unsupported order type {order_type} provided")
    
    if direct:
        order_result = mt5.order_send(request)
        if order_result[0] == 10009:
            print(f"Order for {symbol} successful")
            return order_result[2]
        elif order_result[0] == 10027:
            print("Turn off Algotrading on MT5 Terminal")
            raise Exception("Turn off Algo Trading")
        elif order_result[0] == 10015:
            print(f"Invalid price for {symbol}. Price: {stop_price}")
        elif order_result[0] == 10016:
            print(f"Invalid stops for {symbol}. Stop Loss: {stop_loss}")
        elif order_result[0] == 10014:
            print(f"Invalid volume for {symbol}. Volume {volume}")
        else:
            print("Error lodging order for {symbol}. Error code {order_result[0]}")
            raise Exception("Unknown error lodging order")
    else:
        result = mt5.order_check(request)
        if result[0] == 0:
            print(f"Order check for {symbol} successful. Placing order")
            place_order(
                order_type=order_type,
                symbol=symbol,
                volume=volume,
                stop_price=stop_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                comment=comment,
                direct=True
            )

        elif result[0] == 10015:
            print(f"Invalid price for {symbol}. Price: {stop_price}")


def get_past_data(symbol, timeframe, start, end):
    mt5_timeframe = set_query_timeframe(timeframe)

    rates = mt5.copy_rates_range(
        symbol,
        mt5_timeframe,
        start,
        end
    )
    print(rates)

    dataframe = pd.DataFrame(rates)
    print(dataframe)
    return dataframe