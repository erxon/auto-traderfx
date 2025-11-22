from PyQt5.QtWebEngineWidgets import QWebEngineView
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

class PlotWidget(QWebEngineView):
     def __init__(self, dataframe):
        super().__init__()

        # Initialize Candlesticks data
        if dataframe:
            fig = go.Figure(
                data=[go.Candlestick(x=datetime(dataframe["time"]),
                                    open=dataframe["open"],
                                    high=dataframe["high"],
                                    low=dataframe["low"],
                                    close=dataframe["close"])])

            # Display data
            html_string = fig.to_html(include_plotlyjs='cdn')
            self.setHtml(html_string)
        else:
            self.setHtml("Load some data")
