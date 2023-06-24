import pandas as pd
from yahoo_fin import stock_info as si
from dash import Dash, html, dcc, Input, Output, callback

# get_live_price("ticker") for current data
stock_list = si.tickers_dow()
current_price = None

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Stock Tracker", style={"textAlign": "center"}),
    html.Div("Set Ticker: "),
    dcc.Dropdown(id="stock-dropdown", options=stock_list, style={"width": "40%"}),
    html.Div("Set Lower Limit: "),
    dcc.Input(id="lower-input",type="number", min=0, max=current_price),
    html.Div("Set Upper Limit: "),
    dcc.Input(id="upper-input", type="number", min=current_price, max=1000),
    html.Div("Current Price: "),
    html.Div(id="current-price")
])

@app.callback(
    Output("current-price", "children"),
    Input("stock-dropdown", "value")
)
# Figure out how to update lower and upper limit bounds based on live price
def update_values(stock_ticker):
    global current_price
    current_price = si.get_live_price(stock_ticker)
    return current_price

if __name__ == "__main__":
    app.run()