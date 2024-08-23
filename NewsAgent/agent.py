from news_functions import fetch_news, summarize_news
import json

# Define the request and response models
class NewsRequest(Model):
    company_name: str

class NewsResponse(Model):
    news: str

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"News Agent is running with address: {agent.address}")

@agent.on_query(model=NewsRequest, replies={NewsResponse})
async def handle_news_request(ctx: Context, sender: str, msg: NewsRequest):
    ctx.logger.info(f"Received request to fetch news for: {msg.company_name}")
    
    # Fetch the news articles
    articles = fetch_news(msg.company_name)
    
    # Summarize the news articles
    news_summary = summarize_news(articles)
    
    # Convert the summary to a JSON string
    news_json = json.dumps(news_summary, indent=4)
    
    # Send the response back
    await ctx.send(sender, NewsResponse(news=news_json))

