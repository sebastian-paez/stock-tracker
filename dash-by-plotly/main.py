import pandas as pd
import smtplib
import config
from yahoo_fin import stock_info as si
from dash import Dash, html, dcc, Input, Output, State, callback
from email.message import EmailMessage
from datetime import datetime

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
    dcc.Interval(id="trigger", interval=1000*10), # Updates every 10 seconds
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
    return "$" + str(round(current_price, 2)), current_price, current_price


# Handle submit button
@app.callback(
    Output("submission-error", "children"),
    Output("tracked-stocks", "children"),
    Input("submit-button", "n_clicks"),
    Input("stock-dropdown", "value"),
    Input("lower-input", "value"),
    Input("upper-input", "value"),
    Input("email-address", "value")
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
            return html.Div("ERROR: This stock is already being tracked", style={"font-weight": "bold"}), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        elif lower_limit == None or lower_limit >= current_price or lower_limit < 0:
            return html.Div("ERROR: No lower limit", style={"font-weight": "bold"}), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        elif upper_limit == None or upper_limit <= current_price:
            return html.Div("ERROR: No upper limit", style={"font-weight": "bold"}), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]
        else:
            tracked_tickers.append(stock_ticker)
            tracked_lower.append(lower_limit)
            tracked_upper.append(upper_limit)
            return html.Div(""), [html.Div(children=[html.Div(stock) for stock in tracked_tickers]), 
                html.Div(children=[html.Div("Lower Limit: $" + str(lower)) for lower in tracked_lower]), 
                html.Div(children=[html.Div("Upper Limit: $" + str(upper)) for upper in tracked_upper])]


# # Send email
# @app.callback(
#     Input("trigger", "n_intervals")
# )
# def check_current_price(_, ):
#     i = 0
#     for stock in tracked_tickers:
#         if (si.get_live_price(stock) >= tracked_upper[i]):
#             send_email(email_address, f"{stock} has reached the upper limit of {tracked_upper[i]}", f"Current price of {stock} is {si.get_live_price(stock)}")
#         elif (si.get_live_price(stock) <= tracked_lower[i]):
#             send_email(email_address, f"{stock} has reached the lower limit of {tracked_lower[i]}", f"Current price of {stock} is {si.get_live_price(stock)}")
#         i += 1



if __name__ == "__main__":
    app.run()