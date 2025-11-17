import helper_functions as helper
import mt5_lib

def make_trade(balance, comment, risk_amount, symbol, take_profit, stop_loss, stop_price):
    balance = convert_to_float_and_round(balance, 2)
    take_profit = convert_to_float_and_round(take_profit, 4)
    stop_loss = convert_to_float_and_round(stop_loss, 4)
    stop_price = convert_to_float_and_round(stop_price, 4)

    lot_size = helper.calc_lot_size(
        balance,
        risk_amount,
        stop_loss,
        stop_price,
        symbol
    )

    # Send trade to MT5
    if stop_price > stop_loss:
        trade_type = "BUY_STOP"
    else: 
        trade_type = "SELL_STOP"
    
    trade_outcome = mt5_lib.place_order(
        order_type=trade_type,
        symbol=symbol,
        volume=lot_size,
        stop_loss=stop_loss,
        stop_price=stop_price,
        take_profit=take_profit,
        direct=False
    )
    
    return trade_outcome

# Utility functions
def convert_to_float_and_round(number, decimal):
    converted_to_float = float(number)
    rounded = round(converted_to_float, decimal)
    return rounded