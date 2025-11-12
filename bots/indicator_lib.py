import numpy as np

def calc_custom_ema(dataframe, ema_size):
    # Create the name of the column to be added
    ema_name = "ema_"+str(ema_size)

    # Create the Multiplier
    multiplier = 2 / (ema_size + 1)

    # Calculate the initial value. This will be a single moving average
    initial_mean = dataframe["close"].head(ema_size).mean()

    # Iterate through the dataframe and add the values
    for i in range(len(dataframe)):
        # if i is the size of the EMA, value is the initial mean
        if i == ema_size:
            dataframe.loc[i, ema_name] = initial_mean
        
        # if i is > ema_size, calculate the EMA
        elif i > ema_size:
            ema_value = dataframe.loc[i, "close"] * multiplier + dataframe.loc[i - 1, ema_name] * (1 - multiplier)
            dataframe.loc[i, ema_name] = ema_value
        
        # if i is < ema_size
        else:
            dataframe.loc[i, ema_name] = 0.00
        
    # Once completed, return the completed dataframe
    return dataframe

