import pandas as pd
import smtplib
import config
from yahoo_fin import stock_info as si
from dash import Dash, html, dcc, Input, Output, State, callback
from email.message import EmailMessage

stock_list = si.tickers_dow()
current_price = None
email_address = None
num_clicks = 0
tracked_stocks = []

class Stock:
    def __init__(self, ticker, lower, upper):
        self.ticker = ticker
        self.lower_limit = lower
        self.upper_limit = upper

app = Dash(__name__)
app.layout = html.Div(
    style={"display": "flex", "flexDirection": "column", "alignItems": "center", "justifyContent": "center", "fontFamily": "Helvetica"},
    children=[
    html.H1("Stock Tracker", style={"textAlign": "center"}),
    dcc.Interval(id="trigger", interval=10000, n_intervals=0), # Updates every 10 seconds
    html.Div("Set Ticker: "),
    html.Div(dcc.Dropdown(id="stock-dropdown", options=stock_list, style={"width": "100px", "margin-bottom": "30px"})),
    html.Div("Set Lower Limit: "),
    dcc.Input(id="lower-input",type="number", min=0, max=current_price, style={"margin-bottom": "30px"}),
    html.Div("Set Upper Limit: "),
    dcc.Input(id="upper-input", type="number", min=current_price, max=None, style={"margin-bottom": "30px"}),
    html.Div("Current Price: "),
    html.Div(id="current-price", style={"margin-bottom": "30px"}),
    html.Div("Enter Email Address: "),
    dcc.Input(id="email-address", style={"margin-bottom": "30px"}),
    html.Button("Submit", id="submit-button", n_clicks=0, style={"margin-bottom": "20px"}),
    html.Div(id="submission-error"),
    html.H3("Tracking: "),
    # Set up table
    html.Div(id="tracked-stocks", style={"display": "flex", "flexDirection": "row", "gap": "20px"},
        children=[
            html.Div(children=[html.Div(stock.ticker) for stock in tracked_stocks]),
            html.Div(children=[html.Div("Lower Limit: $" + str(stock.lower_limit)) for stock in tracked_stocks]),
            html.Div(children=[html.Div("Upper Limit: $" + str(stock.upper_limit)) for stock in tracked_stocks]),
            html.Div(children=[html.Div("Current Price: $" + str(round(si.get_live_price(stock.ticker), 2))) for stock in tracked_stocks])]
        )
    ]
)


def send_email(email, subject, body):
    msg = EmailMessage()
    msg["To"] = email
    msg["From"] = config.get_email()
    msg["Subject"] = subject
    msg.set_content(body)

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(config.get_email(), config.get_password())
    server.send_message(msg)
    server.quit()


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
    return "$" + str(round(current_price, 2)), round(current_price, 2), round(current_price, 2)


# Handle submit button
@app.callback(
    Output("submission-error", "children"),
    Input("submit-button", "n_clicks"),
    State("stock-dropdown", "value"),
    State("lower-input", "value"),
    State("upper-input", "value"),
    State("email-address", "value"),
)
def submit_values(n_clicks, stock_ticker, lower_limit, upper_limit, user_email):
    global num_clicks
    global tracked_stocks
    global email_address
    email_address = user_email
    tracked_tickers = []
    for stock in tracked_stocks:
        tracked_tickers.append(stock.ticker)
    if n_clicks > num_clicks:
        num_clicks += 1
        if stock_ticker in tracked_tickers:
            return html.Div("ERROR: This stock is already being tracked", style={"font-weight": "bold"})
        elif lower_limit == None or lower_limit > current_price or lower_limit < 0:
            return html.Div("ERROR: Invalid lower limit", style={"font-weight": "bold"})
        elif upper_limit == None or upper_limit < current_price:
            return html.Div("ERROR: Invalid upper limit", style={"font-weight": "bold"})
        else:
            new_stock = Stock(stock_ticker, lower_limit, upper_limit)
            tracked_stocks.append(new_stock)
            return html.Div("")


# Send email
@app.callback(
    Output("tracked-stocks", "children"),
    Input("trigger", "n_intervals"),
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True
)
def check_current_price(_, n):
    global tracked_stocks
    i = 0
    for stock in tracked_stocks:
        if (round(si.get_live_price(stock.ticker), 2) >= stock.upper_limit):
            send_email(email_address, f"{stock.ticker} has hit your threshold", f"{stock.ticker} has reached your upper limit and is trading at ${stock.lower_limit} per share")
            tracked_stocks.remove(stock)
            return [html.Div(children=[html.Div(stock.ticker) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(stock.lower_limit)) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(stock.upper_limit)) for stock in tracked_stocks]),
                html.Div(children=[html.Div("Current Price: $" + str(round(si.get_live_price(stock.ticker), 2))) for stock in tracked_stocks])]
        elif (round(si.get_live_price(stock.ticker), 2) <= stock.lower_limit):
            send_email(email_address, f"{stock.ticker} has hit your threshold", f"{stock.ticker} has reached your lower limit and is trading at ${stock.lower_limit} per share")
            tracked_stocks.remove(stock)
            return [html.Div(children=[html.Div(stock.ticker) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(stock.lower_limit)) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(stock.upper_limit)) for stock in tracked_stocks]),
                html.Div(children=[html.Div("Current Price: $" + str(si.get_live_price(stock.ticker))) for stock in tracked_stocks])]
        i += 1
    return [html.Div(children=[html.Div(stock.ticker) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(stock.lower_limit)) for stock in tracked_stocks]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(stock.upper_limit)) for stock in tracked_stocks]),
                html.Div(children=[html.Div("Current Price: $" + str(round(si.get_live_price(stock.ticker), 2))) for stock in tracked_stocks])]


if __name__ == "__main__":
    app.run()