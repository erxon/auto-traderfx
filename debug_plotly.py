import mt5_lib
import plotly.graph_objects as go
import pandas as pd

def main():
    print("Connecting to MT5...")
    if not mt5_lib.connect_to_mt5():
        print("Failed to connect to MT5")
        return

    symbol = "USDJPY"
    timeframe = "M30"
    candlesticks = 1000

    print(f"Getting data for {symbol} {timeframe}...")
    try:
        dataframe = mt5_lib.get_candlesticks(symbol, timeframe, candlesticks)
    except Exception as e:
        print(f"Error getting candlesticks: {e}")
        return

    print(f"Dataframe shape: {dataframe.shape}")
    print(dataframe.head())

    if dataframe.empty:
        print("Dataframe is empty!")
        return

    print("Generating Plotly figure...")
    fig = go.Figure(
            data=[go.Candlestick(x=dataframe["time"],
                                open=dataframe["open"],
                                high=dataframe["high"],
                                low=dataframe["low"],
                                close=dataframe["close"])])
    
    print("Converting to HTML...")
    html_string = fig.to_html(include_plotlyjs=True, full_html=True)
    
    output_file = "debug_standalone.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_string)
    
    print(f"Saved HTML to {output_file}")
    print("Done.")

if __name__ == "__main__":
    main()
