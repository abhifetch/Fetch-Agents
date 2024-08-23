from ai_engine import UAgentResponse, UAgentResponseType
from functions import get_indicator, calculate_signal, analyze_stock, summarize_signals
from uagents import Model, Protocol, Context
from pydantic import Field
import requests
import json

class TechAnalysisRequest(Model):
    company_name: str 

async def get_symbol(company_name):
    url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company_name}&apikey={API_KEY}"

    response = requests.get(url)
    data = response.json()

    if 'bestMatches' in data and data['bestMatches']:
        first_match = data['bestMatches'][0]
        symbol = first_match['1. symbol']
        return symbol
    else:
        return f"No symbol found for {company_name}."

async def get_technical_summary(symbol):
    results = analyze_stock(symbol)
    print(results)
    summary = summarize_signals(results)
    return summary

tech_analysis_agent = Protocol("Technical Analysis", version="2.1")

@tech_analysis_agent.on_message(model=TechAnalysisRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, msg: TechAnalysisRequest):
    ctx.logger.info(f"Got request from {sender} for technical analysis: {msg.company_name}")

    try:
        symbol = await get_symbol(msg.company_name)
        ctx.logger.info(f"Symbol: {symbol}")

        if "No symbol found" in symbol:
            raise Exception(symbol)

        summary = await get_technical_summary(symbol)
        await ctx.send(sender, UAgentResponse(message=str(summary), type=UAgentResponseType.FINAL))
    except Exception as ex:
        ctx.logger.info(f"Exception: {str(ex)}")
        await ctx.send(sender, UAgentResponse(message=str('function is unsuccessful'), type=UAgentResponseType.FINAL))

# Include protocol to the agent
agent.include(tech_analysis_agent)

