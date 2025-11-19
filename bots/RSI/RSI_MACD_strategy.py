import ta
import mt5_lib
import helper_functions as helper

def rsi_macd_strategy(symbol, timeframe, backtest_data=None, risk_amount=0.01, balance=100000):
    
    """
    This function implements the RSI-MACD strategy. It takes in a symbol, timeframe, optional backtest data, risk amount and balance, and returns a boolean indicating whether a trade was made.

    The function first retrieves the data for the symbol and timeframe (or uses the backtest data if provided). It then calculates the indicators and generates the trade signals. Finally, it calculates the lot size and makes the actual trade.

    Parameters:
        symbol (str): the symbol of the currency pair to be traded.
        timeframe (str): the timeframe of the data to be retrieved (e.g. "M1", "M5", "M15", etc.).
        backtest_data (pandas.DataFrame, optional): the backtest data to be used instead of retrieving new data. Defaults to None.
        risk_amount (float, optional): the amount of balance to risk in each trade. Defaults to 0.01.
        balance (float, optional): the current balance of the trading account. Defaults to 100000.

    Returns:
        bool: whether a trade was made or not.
    """
    
    dataframe = get_data(symbol=symbol, timeframe=timeframe)
    
    if (backtest_data is not None):
        dataframe = backtest_data

    dataframe = calc_indicators(dataframe=dataframe)

    dataframe = get_signals(dataframe=dataframe, symbol=symbol)

    dataframe = sl_tp_calc(
        dataframe=dataframe,
        symbol=symbol
    )

    dataframe = lot_size_calc(
        dataframe=dataframe,
        balance=balance,
        risk_amount=risk_amount,
        symbol=symbol
    )

    # Make the actual trade
    trade_event = dataframe.tail(1).copy()
    print(trade_event)
    
    if trade_event["buy_signal"].values or trade_event["sell_signal"].values:
        comment_string = f"RSI_MACD_Strategy_{symbol}"

        trade_outcome = mt5_lib.place_order(
            order_type="BUY_STOP" if trade_event["buy_signal"].values else "SELL_STOP",
            symbol=symbol,
            volume=trade_event['lot_size'].values,
            stop_loss=trade_event['stop_loss'].values,
            take_profit=trade_event['take_profit'].values,
            comment=comment_string,
            stop_price=trade_event['close'].values,
            direct=False
        )
    else:
        trade_outcome = False

    return trade_outcome

def get_signals(dataframe, symbol):

    """
    This function generates buy and sell signals based on RSI and MACD indicators.

    Parameters
    ----------
    dataframe : pandas.DataFrame
        The dataframe containing the RSI and MACD indicators.
    symbol : str
        The symbol of the currency pair to be traded.

    Returns
    -------
    pandas.DataFrame
        The dataframe with the additional columns 'buy_signal' and 'sell_signal'.
    """
    dataframe["buy_signal"] = (
        (dataframe["rsi"].shift(1) < 30) &
        (dataframe["rsi"] > 30) &
        (dataframe["macd"] > dataframe["signal"]) &
        (dataframe["hist"] > 0)
    )

    dataframe["sell_signal"] = (
        (dataframe["rsi"].shift(1) > 70) &
        (dataframe["rsi"] < 70) &
        (dataframe["macd"] < dataframe["signal"]) &
        (dataframe["hist"] < 0)
    )

    return dataframe

def lot_size_calc(dataframe, balance, risk_amount, symbol):
    """
    This function calculates the lot size for each trade signal based on the given balance, risk amount, stop loss and entry price.

    :param dataframe: The dataframe containing the trade signals, stop loss, entry price and other relevant columns.
    :type dataframe: pandas.DataFrame
    :param balance: The current balance of the trading account.
    :type balance: float
    :param risk_amount: The amount of balance to risk in each trade.
    :type risk_amount: float
    :param symbol: The symbol of the currency pair to be traded.
    :type symbol: str
    :return: The dataframe with the lot size added.
    :rtype: pandas.DataFrame
    """

    for i in range(len(dataframe)):
        if dataframe.loc[i, 'buy_signal'] or dataframe.loc[i, 'sell_signal']:
            stop_loss = dataframe.loc[i, 'stop_loss']
            entry_price = dataframe.loc[i, 'close']

            lot_size = helper.calc_lot_size(
                balance=balance,
                risk_amount=risk_amount,
                stop_loss=stop_loss,
                stop_price=entry_price,
                symbol=symbol
            )

            dataframe.loc[i, 'lot_size'] = lot_size
        else:
            dataframe.loc[i, 'lot_size'] = 0.00

    return dataframe
def sl_tp_calc(dataframe, symbol, balance=100000, risk_amount=0.01):


    """
    This function calculates the stop loss and take profit for each trade signal based on the given balance, risk amount, symbol and dataframe.

    :param dataframe: The dataframe containing the trade signals and other relevant columns.
    :type dataframe: pandas.DataFrame
    :param symbol: The symbol of the currency pair to be traded.
    :type symbol: str
    :param balance: The current balance of the trading account.
    :type balance: float, default=100000
    :param risk_amount: The amount of balance to risk in each trade.
    :type risk_amount: float, default=0.01
    :return: The dataframe with the stop loss and take profit added.
    :rtype: pandas.DataFrame
    """

    for i in range(len(dataframe)):
        if i < 14:
            dataframe.loc[i, 'atr'] = 0.00
        else:
            dataframe.loc[i, 'atr'] = ta.volatility.average_true_range(
                dataframe['high'].iloc[i-14:i],
                dataframe['low'].iloc[i-14:i],
                dataframe['close'].iloc[i-14:i],
                window=14
            ).iloc[-1]

            entry_price = dataframe.loc[i, 'close']

            # Compute SL & TP
            if dataframe.loc[i, 'buy_signal']:
                dataframe.loc[i, 'stop_loss'] = helper.convert_to_float_and_round(entry_price - (dataframe.loc[i, 'atr'] * 1.5), symbol)
                dataframe.loc[i, 'take_profit'] = helper.convert_to_float_and_round(entry_price + (dataframe.loc[i, 'atr'] * 3), symbol)
            elif dataframe.loc[i, 'sell_signal']:
                dataframe.loc[i, 'stop_loss'] = helper.convert_to_float_and_round(entry_price + (dataframe.loc[i, 'atr'] * 1.5), symbol)
                dataframe.loc[i, 'take_profit'] = helper.convert_to_float_and_round(entry_price - (dataframe.loc[i, 'atr'] * 3), symbol)

    return dataframe

def get_data(symbol, timeframe):
    data = mt5_lib.get_candlesticks(symbol=symbol, timeframe=timeframe, number_of_candles=2000)
    return data

def calc_indicators(dataframe):
    """  
    This calculates indicators for RSI & MACD 
    """

    dataframe["rsi"] = ta.momentum.rsi(dataframe["close"], window=14)
    macd = ta.trend.MACD(dataframe["close"])
    dataframe["macd"] = macd.macd()
    dataframe["signal"] = macd.macd_signal()
    dataframe["hist"] = macd.macd_diff()

    return dataframe