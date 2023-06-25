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
    dcc.Dropdown(id="stock-dropdown", options=stock_list, style={"width": "40%", "margin-bottom": "30px"}),
    html.Div("Set Lower Limit: "),
    dcc.Input(id="lower-input",type="number", min=0, max=current_price, style={"margin-bottom": "30px"}),
    html.Div("Set Upper Limit: "),
    dcc.Input(id="upper-input", type="number", min=current_price, max=1000, style={"margin-bottom": "30px"}),
    html.Div("Current Price: "),
    html.Div(id="current-price", style={"margin-bottom": "30px"}),
    html.Button("Submit", id="submit-button", n_clicks=0),
])


# Handle selected ticker
@app.callback(
    Output("current-price", "children"),
    Output("lower-input", "max"),
    Output("upper-input", "min"),
    Input("stock-dropdown", "value"),
)
def update_values(stock_ticker):
    global current_price
    current_price = si.get_live_price(stock_ticker)
    return current_price, current_price, current_price


# Handle submit button
@app.callback(
    Output("submit-button", "n_clicks"),
    Output("stock-dropdown", "value"),
    Output("lower-input", "value"),
    Output("upper-input", "value"),
    Input("submit-button", "n_clicks")
)
def submit_values(n_clicks):
    if n_clicks != 0 or n_clicks != None:
        # Add to tracked stocks here
        # Figure out how to remove current price value when submitted
        return None, None, None, None



if __name__ == "__main__":
    app.run()