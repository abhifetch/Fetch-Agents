from uagents import Agent, Context, Model
import json
import requests
import datetime

# Replace with your actual API key
API_KEY = 'YOUR API KEY'

# Define the PriceRequest and PriceResponse models
class PriceRequest(Model):
    ticker: str
    interval: str = "DAILY"
    range_start: str = None
    range_end: str = None

class PriceResponse(Model):
    prices: str  # JSON string of prices

# Define the function to fetch prices
def fetch_prices(ticker, interval="DAILY", range_start=None, range_end=None):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_{interval}&symbol={ticker}&apikey={API_KEY}'
    
    if interval == "INTRADAY":
        url += "&interval=5min"

    r = requests.get(url)
    data = r.json()

    if interval == "DAILY":
        time_series_key = "Time Series (Daily)"
    elif interval == "INTRADAY":
        time_series_key = "Time Series (5min)"

    filtered_data = {}

    if time_series_key in data:
        for date_str, price_data in data[time_series_key].items():
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            
            if range_start:
                range_start_date = datetime.datetime.strptime(range_start, '%Y-%m-%d')
                if date_obj < range_start_date:
                    continue
            
            if range_end:
                range_end_date = datetime.datetime.strptime(range_end, '%Y-%m-%d')
                if date_obj > range_end_date:
                    continue

            filtered_data[date_str] = price_data

    return json.dumps(filtered_data, indent=4)

# Initialize the agent
agent = Agent(name="stock_price_agent", port=8000)

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"With address: {agent.address}")
    ctx.logger.info(f"And wallet address: {agent.wallet.address()}")

# Handle incoming queries
@agent.on_query(model=PriceRequest, replies={PriceResponse})
async def handle_price_request(ctx: Context, sender: str, msg: PriceRequest):
    ctx.logger.info(f'User has requested prices for ticker: {msg.ticker}')
    prices_json = fetch_prices(msg.ticker, msg.interval, msg.range_start, msg.range_end)
    ctx.logger.info(prices_json)
    await ctx.send(sender, PriceResponse(prices=prices_json))

if __name__ == "__main__":
    agent.run()

