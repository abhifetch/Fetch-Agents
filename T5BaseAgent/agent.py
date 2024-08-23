from ai_engine import UAgentResponse, UAgentResponseType
from uagents import Model
from pydantic import Field
import requests

T5_BASE_URL = "http://35.193.76.249:8080/translate"

HEADERS = {
    "Accept": "*/*",
    "User-Agent": "t5-base agentverse (https://agentverse.ai/)",
    "Content-Type": "application/json"
}

class TranslationRequest(Model):
    input_text: str = Field(alias="You are interested in translating the below text", description="text you want to translate. supported languages are English, French, Romanian, German")

t5_base_agent = Protocol("T5 Language Translator", version="1.0.1")

@t5_base_agent.on_message(model=TranslationRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, request: TranslationRequest):
    # Log the request details
    ctx.logger.info(f"Got request from to translate from {sender}")

    try:
        payload = {
            "sender": sender,
            "input_text": request.input_text
        }
        
        response = requests.post(T5_BASE_URL, headers=HEADERS, json=payload)
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

# publish_manifest will make the protocol details available on agentverse.
agent.include(t5_base_agent)

