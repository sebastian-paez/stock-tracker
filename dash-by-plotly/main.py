import pandas as pd
from yahoo_fin import stock_info as si
from dash import Dash, html, dcc, Input, Output, callback

stock_list = si.tickers_dow()
current_price = None
num_clicks = 0
tracked_tickers = []
tracked_lower = []
tracked_upper = []

app = Dash(__name__)
app.layout = html.Div([
    html.H1("Stock Tracker", style={"textAlign": "center"}),
    html.Div("Set Ticker: "),
    dcc.Dropdown(id="stock-dropdown", options=stock_list, style={"width": "40%", "margin-bottom": "30px"}),
    html.Div("Set Lower Limit: "),
    dcc.Input(id="lower-input",type="number", min=0, max=current_price, style={"margin-bottom": "30px"}),
    html.Div("Set Upper Limit: "),
    dcc.Input(id="upper-input", type="number", min=current_price, max=None, style={"margin-bottom": "30px"}),
    html.Div("Current Price: "),
    html.Div(id="current-price", style={"margin-bottom": "30px"}),
    html.Button("Submit", id="submit-button", n_clicks=0, style={"margin-bottom": "30px"}),
    html.Div(id="submission-error", style={"margin-bottom": "30px"}),
    html.H3("Tracking: "),
    # Set up table
    html.Div(id="tracked-stocks", style={"display": "flex", "flexDirection": "row", "gap": "20px"},
        children=[
            html.Div(children=[html.Div(stock) for stock in tracked_tickers]),
            html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]),
            html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper]),
        ]
    )
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
    return "$" + str(round(current_price, 2)), current_price, current_price


# Handle submit button
@app.callback(
    Output("submission-error", "children"),
    Output("tracked-stocks", "children"),
    Input("submit-button", "n_clicks"),
    Input("stock-dropdown", "value"),
    Input("lower-input", "value"),
    Input("upper-input", "value")
)
def submit_values(n_clicks, stock_ticker, lower_limit, upper_limit):
    global num_clicks
    global tracked_tickers
    global tracked_lower
    global tracked_upper
    if n_clicks > num_clicks:
        num_clicks += 1
        if stock_ticker in tracked_tickers:
            return html.Div("ERROR: This stock is already being tracked"), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        elif lower_limit == None or lower_limit >= current_price:
            return html.Div("ERROR: No lower limit"), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        elif upper_limit == None or upper_limit <= current_price:
            return html.Div("ERROR: No upper limit"), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        else:
            tracked_tickers.append(stock_ticker)
            tracked_lower.append(lower_limit)
            tracked_upper.append(upper_limit)
            return html.Div(""), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        


if __name__ == "__main__":
    app.run()