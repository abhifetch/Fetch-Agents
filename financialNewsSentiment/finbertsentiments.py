# old agent : agent1q0rd3mq72ukn0ndewklfh3e3ytwq63xefxe5h56ypx6durrs9l2772kg2j4


from ai_engine import UAgentResponse, UAgentResponseType
from uagents import Model
from pydantic import Field
import requests
import json

FINBERT_URL = "http://35.193.76.249:3000/get_sentiment"

HEADERS = {
    "Accept": "*/*",
    "User-Agent": "agentverse (https://agentverse.ai/)",
    "Content-Type": "application/json"
}

class FinBertRequest(Model):
    input_text: str = Field(alias="You are interested in analyzing sentiment in the market about", description="your text that can be financial news, particularly news related to predicting the behavior and possible trend of stock markets")

finbert_agent = Protocol("FinBert Protocol", version="2.0.1")

@finbert_agent.on_message(model=FinBertRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, request: FinBertRequest):
    ctx.logger.info(f"Got request from  {sender} for text classification : {request.input_text}")

    try:
        payload = {
            "sender": sender,
            "input_text": request.input_text
        }
        
        response = requests.post(FINBERT_URL, headers=HEADERS, json=payload)
        if response.status_code == 200:
            ctx.logger.info(f"code 200: {response.json()}")
            if response.json()["status"] == "success":
                ctx.logger.info(f"Success: {response.json()}")
                await ctx.send(sender, UAgentResponse(message=f"{response.json()['message']}", type=UAgentResponseType.FINAL))
            else:
                ctx.logger.info(f"Failed: {response.json()}")
                await ctx.send(sender, UAgentResponse(message=f"Error: {response.json()['message']}", type=UAgentResponseType.ERROR))
        else:
            ctx.logger.info(f"Failed Not Code 200: {response.content}")
            await ctx.send(sender, UAgentResponse(message=f"Error: {response.content}", type=UAgentResponseType.ERROR))
    except Exception as ex:
        ctx.logger.info(f"Exception: {str(ex)}")
        await ctx.send(sender, UAgentResponse(message=str(ex), type=UAgentResponseType.ERROR))

# Include protocol to the agent
agent.include(finbert_agent)
