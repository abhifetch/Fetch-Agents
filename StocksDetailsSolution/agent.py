# import required libraries
import requests
from ai_engine import UAgentResponse, UAgentResponseType

# Define a data model for getting nutrition request
class StocksRequest(Model):
    company_name : str
    stock_price : str
    tech_analysis : str
    sentiment : str

stocks_protocol = Protocol('Stocks details protocol')

@stocks_protocol.on_message(model=StocksRequest, replies=UAgentResponse)
async def on_nutrient_request(ctx: Context, sender: str, msg: StocksRequest):
    ctx.logger.info(f"Received Stocks details request from {sender} with recipe name: {msg.company_name}")
    response = f'The stock price for {msg.company_name} is {msg.stock_price} \nIndicators: {msg.tech_analysis} \nOverall Snetiment: {msg.sentiment}'
    ctx.logger.info(response)
    await ctx.send(sender, UAgentResponse(message=response, type=UAgentResponseType.FINAL))

agent.include(stocks_protocol)

