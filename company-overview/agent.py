import os
import requests
from uagents import Agent, Context, Model, Protocol
from uagents.models import ErrorMessage
from functions import fetch_overview_json

AGENT_SEED = os.getenv("AGENT_SEED", "company-overview")

class CompanyOverviewRequest(Model):
    ticker: str

class CompanyOverviewResponse(Model):
    overview: str


PORT = 8000
agent = Agent(
    seed=AGENT_SEED,
    port=PORT,
    endpoint=f"http://localhost:{PORT}/submit",
)

proto = Protocol(name="Companyoverview", version="0.1.0")


@agent.on_event("startup")
async def introduce(ctx: Context):
    ctx.logger.info(ctx.agent.address)


@proto.on_message(CompanyOverviewRequest, replies={CompanyOverviewResponse, ErrorMessage})
async def handle_request(ctx: Context, sender: str, msg: CompanyOverviewRequest) -> CompanyOverviewResponse:
    ctx.logger.info(f"Recieved company overview request for ticker : {msg.ticker}")
    try:
        output_json = fetch_overview_json(msg.ticker)
        ctx.logger.info(f'Company overview for ticker {msg.ticker} is ${output_json}')
    except Exception as err:
        ctx.logger.error(err)
        await ctx.send(
            sender,
            ErrorMessage(
                error="An error occurred while processing the request. Please try again later."
            ),
        )
        return
    await ctx.send(sender, CompanyOverviewResponse(overview = str(output_json)))

agent.include(proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
