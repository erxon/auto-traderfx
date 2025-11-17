def calc_lot_size(balance, risk_amount, stop_loss, stop_price, symbol):
    amount_to_risk = balance * risk_amount

    symbol_name = symbol.split(".")
    symbol_name = symbol_name[0]

    if symbol == "USDJPY":
        pip_size = 0.01
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        pip_value = amount_to_risk / stop_pips_integer
        pip_value = pip_value * stop_price
        raw_lot_size = pip_value / 1000
    
    elif symbol == "USDCAD":
        pip_size = 0.0001
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        pip_value = amount_to_risk / stop_pips_integer
        pip_value = pip_value * stop_price
        raw_lot_size = pip_value / 10
    else:
        pip_size = 0.0001
        stop_pips_integer = abs((stop_price - stop_loss) / pip_size)
        pip_value = amount_to_risk / stop_pips_integer
        raw_lot_size = pip_value / 10


    lot_size = float(raw_lot_size)
    lot_size = round(lot_size, 2)

    if lot_size >= 10:
        lot_size = 9.99


    return lot_size


