from uagents import Agent, Context, Model
import requests
import openai

# Define Request Data Model
class TickerRequest(Model):
    company: str

class TickerResponse(Model):
    ticker : str

openai.api_key = OPENAI_API_KEY

async def get_verified_ticker(company_name, context):
    """
    Fetches ticker symbols for a given company name and verifies the most relevant one using OpenAI's GPT-4 model.
    
    Args:
        company_name (str): The name of the company to search for.
        api_key (str): Your Alpha Vantage API key.
        
    Returns:
        str: The verified ticker symbol.
    """
    context.logger.info(company_name)
    # Fetch ticker symbols using Alpha Vantage API
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={API_KEY}'
    r = requests.get(url)
    data = r.json()
    context.logger.info(data)
    # Collect the first 5 ticker symbols
    ticker_list = []
    for i in range(min(5, len(data.get('bestMatches', [])))):
        ticker = data.get('bestMatches')[i].get('1. symbol')
        ticker_list.append(ticker)
    
    #if not ticker_list:
        #return "No ticker symbols found."
    
    # Verify the correct ticker using OpenAI's GPT-4
    response = openai.chat.completions.create(
        model="gpt-4",  # You can also use "gpt-3.5-turbo" if preferred
        messages=[
            {"role": "system", "content": "You are an agent to provide tickers for a given company name. You will get 5 best matching tickers in a list and you have to verify which ticker is right. Just respond always with a ticker. For example: TSLA for Tesla, AAPL for Apple, etc. If the list is empty check ticker for {company_name } and return ticker"},
            {"role": "user", "content": f'ticker_list : {str(ticker_list)} company name : {company_name}'}
        ]
    )
    
    # Extract and return the verified ticker
    verified_ticker = response.choices[0].message.content
    return verified_ticker


@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"With address: {agent.address}")
    ctx.logger.info(f"And wallet address: {agent.wallet.address()}")

@agent.on_query(model=TickerRequest, replies={TickerResponse})
async def handle_song_request(ctx: Context, sender: str, msg: TickerRequest):
    ctx.logger.info(f'User has requested to search ticker for company: {msg.company}')
    ticker = await get_verified_ticker(msg.company, ctx)
    ctx.logger.info(ticker)
    await ctx.send(sender, TickerResponse(ticker=str(ticker)))
