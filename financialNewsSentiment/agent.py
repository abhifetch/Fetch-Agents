from ai_engine import UAgentResponse, UAgentResponseType
from uagents import Model, Context, Protocol
from pydantic import Field
import requests
import json

class FinBertRequest(Model):
    company_name: str

finbert_agent = Protocol("FinBert Protocol", version="2.0.1")

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

async def get_news_titles(symbol):
    # Fetch news articles related to the stock symbol
    news_url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={API_KEY}"
    news_response = requests.get(news_url)
    news_data = news_response.json()

    if 'feed' not in news_data:
        return "Error: Unable to fetch news articles."

    news_articles = news_data['feed']
    if not news_articles:
        return "Error: No news articles found."

    # Extract headlines from news articles
    headlines = [article['title'] for article in news_articles]

    # Concatenate headlines into a single string
    combined_headlines = " ".join(headlines)
    return combined_headlines


async def get_news_sentiment(headlines):
    # Analyze sentiment using FinBERT
    API_URL = "https://api-inference.huggingface.co/models/ProsusAI/finbert"
    headers = {"Authorization": f"Bearer {HF_KEY}"}

    payload = {"inputs": headlines}
    response = requests.post(API_URL, headers=headers, json=payload)
    print(response)
    sentiment_data = response.json()
    sentiment_scores = sentiment_data[0]
    overall_sentiment = max(sentiment_scores, key=lambda x: x['score'])['label']
    formatted_scores = ", ".join([f"{score['label']}: {score['score']:.2f}" for score in sentiment_scores])
    
    return f"Overall sentiment: {overall_sentiment}. with scores: {formatted_scores}."

@finbert_agent.on_message(model=FinBertRequest, replies={UAgentResponse})
async def handle_request(ctx: Context, sender: str, request: FinBertRequest):
    ctx.logger.info(f"Got request from {sender} for text classification: {request.company_name}")

    try:
        # Get the stock symbol
        symbol = await get_symbol(request.company_name)
        ctx.logger.info(f"Got symbol: {symbol}")

        if "No symbol found" in symbol:
            raise Exception(symbol)

        # Get news titles
        news_titles = await get_news_titles(symbol)
        if "Error" in news_titles:
            raise Exception(news_titles)
        ctx.logger.info(f"Collected news titles: {news_titles}")

        # Get sentiment analysis
        sentiment_score = await get_news_sentiment(news_titles[:200])
        if "Error" in sentiment_score:
            raise Exception(sentiment_score)
        ctx.logger.info(f"Sentiment analysis result: {str(sentiment_score)}")

        # Send response back
        await ctx.send(sender, UAgentResponse(message=str(sentiment_score), type=UAgentResponseType.FINAL))
    except Exception as ex:
        ctx.logger.error(f"Exception: {str(ex)}")
        await ctx.send(sender, UAgentResponse(message=str(ex), type=UAgentResponseType.ERROR))

# Include protocol to the agent
agent.include(finbert_agent)

