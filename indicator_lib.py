import numpy as np
import ta

def calc_custom_ema(dataframe, ema_size):
    ema_name = "ema_"+str(ema_size)
    multiplier = 2 / (ema_size + 1)
    initial_mean = dataframe["close"].head(ema_size).mean()

    for i in range(len(dataframe)):
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        elif i > ema_size:
            ema_value = dataframe.loc[i, "close"] * multiplier + dataframe.loc[i - 1, ema_name] * (1 - multiplier)
            dataframe.loc[i, ema_name] = ema_value
        else:
            dataframe.loc[i, ema_name] = 0.00

    return dataframe

def ema_cross_calculator(dataframe, ema_one, ema_two):
    ema_one_column = "ema_" + str(ema_one)
    ema_two_column = "ema_" + str(ema_two)

    dataframe["position"] = dataframe[ema_one_column] > dataframe[ema_two_column]
    dataframe["pre_position"] = dataframe["position"].shift(1)
    dataframe.dropna(inplace=True)

    dataframe["ema_cross"] = dataframe["position"] != dataframe["pre_position"]
    dataframe.drop(columns=["position", "pre_position"], inplace=True)

    return dataframe

