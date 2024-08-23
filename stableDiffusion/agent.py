from ai_engine import UAgentResponse, UAgentResponseType
from uagents import Model
from pydantic import Field
import requests
import json

class SDRequest(Model):
    image_desc: str = Field(alias="image description", description="your sentence describing the image you want to generate")

STABLE_DIFFUSION_URL = "http://35.193.76.249:8000/get_image"

HEADERS = {
    "Accept": "*/*",
    "User-Agent": "fetch agentverse (https://canary.agentverse.ai/)",
    "Content-Type": "application/json"
}

# Create a protocol named "Request"
stable_diffusion_agent = Protocol("Stable Diffusion Image Generator", version="2.0.6")

@stable_diffusion_agent.on_message(model=SDRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, request: SDRequest):
    # Log the request details
    ctx.logger.info(f"Got request from  {sender} to auto complete this: {request.image_desc}")

    # Make the HTTP request and handle possible errors
    try:
        payload = {
            "sender": sender,
            "image_desc": request.image_desc
        }
        print("final payload", payload)
        response = requests.post(STABLE_DIFFUSION_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            try:
                response_json = response.json()
                ctx.logger.info(f"Code 200: {response_json}")
                if 'image_url' in response_json:
                    image_url = response_json['image_url']
                    anchor_tag = f'<a href="{image_url}">Click here to view your image</a>'
                    await ctx.send(sender, UAgentResponse(message=f"Your image is created! {anchor_tag}", type=UAgentResponseType.FINAL))
                else:
                    await ctx.send(sender, UAgentResponse(message="Unexpected response format", type=UAgentResponseType.ERROR))
            except json.JSONDecodeError:
                ctx.logger.info("Failed to decode JSON response")
                await ctx.send(sender, UAgentResponse(message="Failed to decode JSON response from server", type=UAgentResponseType.ERROR))
        else:
            ctx.logger.info(f"Error: {response.content}")
            await ctx.send(sender, UAgentResponse(message=f"Error: {response.content}", type=UAgentResponseType.ERROR))
    except Exception as ex:
        ctx.logger.info(f"Exception: {str(ex)}")
        await ctx.send(sender, UAgentResponse(message=str(ex), type=UAgentResponseType.ERROR))

# Include the protocol with the agent
agent.include(stable_diffusion_agent)

