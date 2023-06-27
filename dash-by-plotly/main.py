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
tracked_tickers = []
tracked_lower = []
tracked_upper = []

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
            html.Div(children=[html.Div(stock) for stock in tracked_tickers]),
            html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]),
            html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper]),
        ]
        ),
    html.H3(id="placeholder", style={"margin-top": "30px"})
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
    global tracked_tickers
    global tracked_lower
    global tracked_upper
    global email_address
    email_address = user_email
    if n_clicks > num_clicks:
        num_clicks += 1
        if stock_ticker in tracked_tickers:
            return html.Div("ERROR: This stock is already being tracked", style={"font-weight": "bold"})
        elif lower_limit == None or lower_limit > current_price or lower_limit < 0:
            return html.Div("ERROR: Invalid lower limit", style={"font-weight": "bold"})
        elif upper_limit == None or upper_limit < current_price:
            return html.Div("ERROR: Invalid upper limit", style={"font-weight": "bold"})
        else:
            tracked_tickers.append(stock_ticker)
            tracked_lower.append(lower_limit)
            tracked_upper.append(upper_limit)
            return html.Div("")


# Send email
@app.callback(
    Output("placeholder", "children"),
    Output("tracked-stocks", "children"),
    Input("trigger", "n_intervals"),
    Input("submit-button", "n_clicks"),
    prevent_initial_call=True
)
def check_current_price(_, n):
    global tracked_tickers
    global tracked_lower
    global tracked_upper
    i = 0
    for stock in tracked_tickers:
        if (round(si.get_live_price(stock), 2) >= tracked_upper[i]):
            send_email(email_address, f"{stock} has hit your threshold", f"{stock} has reached your upper limit and is trading at ${tracked_lower[i]} per share")
            tracked_tickers.remove(stock)
            tracked_lower.remove(tracked_lower[i])
            tracked_upper.remove(tracked_upper[i])
            return html.Div(f"Upper Limit Reached for {stock}"), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        elif (round(si.get_live_price(stock), 2) <= tracked_lower[i]):
            send_email(email_address, f"{stock} has hit your threshold", f"{stock} has reached your lower limit and is trading at ${tracked_lower[i]} per share")
            tracked_tickers.remove(stock)
            tracked_lower.remove(tracked_lower[i])
            tracked_upper.remove(tracked_upper[i])
            return html.Div(f"Lower Limit Reached for {stock}"), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper]),
                html.Div(children=[html.Div("Current Price: $" + str(si.get_live_price(ticker))) for ticker in tracked_tickers])]
        i += 1
    return "", [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper]),
                html.Div(children=[html.Div("Current Price: $" + str(round(si.get_live_price(ticker), 2))) for ticker in tracked_tickers])]


if __name__ == "__main__":
    app.run()