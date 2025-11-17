import mt5_lib
import indicator_lib
import make_trade

def ema_cross_strategy(symbol, timeframe, ema_one, ema_two, balance, amount_to_risk):

    data = get_data(symbol=symbol, timeframe=timeframe)

    data = calc_indicators(
        data=data,
        ema_one=ema_one,
        ema_two=ema_two
    )

    data = det_trade(
        data=data,
        ema_one=ema_one,
        ema_two=ema_two
    )

    trade_event = data.tail(1).copy()

    if trade_event["ema_cross"].values:
        comment_string = f"EMA_Cross_Strategy_{symbol}"
        print(comment_string)
        make_trade_outcome = make_trade.make_trade(
            balance=balance,
            comment=comment_string,
            risk_amount=amount_to_risk,
            symbol=symbol,
            take_profit=trade_event['take_profit'].values,
            stop_price=trade_event['stop_price'].values,
            stop_loss=trade_event['stop_loss'].values,
        )

    else:
        make_trade_outcome = False
    
    return make_trade_outcome


def calc_indicators(data, ema_one, ema_two):
    dataframe = indicator_lib.calc_custom_ema(
        dataframe=data,
        ema_size=ema_one

    )

    dataframe = indicator_lib.calc_custom_ema(
        dataframe=dataframe,
        ema_size=ema_two
    )

    dataframe = indicator_lib.ema_cross_calculator(
        dataframe= dataframe,
        ema_one=ema_one,
        ema_two=ema_two
    )

    

    return dataframe

def get_data(symbol, timeframe):
    data = mt5_lib.get_candlesticks(symbol=symbol, timeframe=timeframe, number_of_candles=1000)
    return data

def det_trade(data, ema_one, ema_two):
    ema_one_column = "ema_"+str(ema_one)
    ema_two_column = "ema_"+str(ema_two)

    if ema_one > ema_two:
        ema_column = ema_one_column
        min_value = ema_one
    elif ema_two > ema_one:
        ema_column = ema_two_column
        min_value = ema_two
    else:
        raise ValueError("EMA values are the same")
    
    dataframe = data.copy()

    dataframe["take_profit"] = 0.00
    dataframe["stop_price"] = 0.00
    dataframe["stop_loss"] = 0.00

    for i in range(len(dataframe)):
        if i <= min_value:
            continue
        else:
            if dataframe.loc[i, 'ema_cross']:
                if dataframe.loc[i, 'open'] < dataframe.loc[i, 'close']:
                    stop_loss = dataframe.loc[i, ema_column]
                    stop_price = dataframe.loc[i, 'high']
                    distance = stop_price - stop_loss
                    take_profit = stop_price + distance
                else:
                    stop_loss = dataframe.loc[i, ema_column]
                    stop_price = dataframe.loc[i, 'low']
                    distance = stop_loss - stop_price
                    take_profit = stop_price - distance

                dataframe.loc[i, 'stop_loss'] = stop_loss
                dataframe.loc[i, 'stop_price'] = stop_price
                dataframe.loc[i, 'take_profit'] = take_profit


    return dataframe