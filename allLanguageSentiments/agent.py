from uagents import Agent, Context, Model
import openai

# Define Request Data Model
class SentimentRequest(Model):
    text: str

class SentimentResponse(Model):
    sentiment : str

@agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info(f"With address: {agent.address}")
    ctx.logger.info(f"And wallet address: {agent.wallet.address()}")

openai.api_key = OPENAI_API_KEY

async def translate_to_english(text):
    """
    Translates the given text to English using OpenAI's GPT-4 model.
    
    Args:
        text (str): The text to be translated.
        
    Returns:
        str: The translated text in English.
    """
    response = openai.chat.completions.create(
        model="gpt-4",  # You can also use "gpt-3.5-turbo" if preferred
        messages=[
            {"role": "system", "content": "You are a translator. Translate the following text to English."},
            {"role": "user", "content": text}
        ]
    )
    
    # Extract and return the translated text
    return response.choices[0].message.content



async def analyze_sentiment_huggingface(text):
    """
    Analyzes the sentiment of the given text using Hugging Face's heBERT sentiment analysis model.
    
    Args:
        text (str): The text to be analyzed for sentiment.
        
    Returns:
        str: The label of the top sentiment (e.g., Positive, Negative, Neutral).
    """

    # Define the Hugging Face API endpoint and headers with your API key
    API_URL = "https://api-inference.huggingface.co/models/avichr/heBERT_sentiment_analysis"
    headers = {"Authorization": "Bearer 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"}

    payload = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=payload)
    response_json = response.json()

    # Extract the sentiment with the highest score
    top_sentiment = max(response_json[0], key=lambda x: x['score'])
    
    return top_sentiment['label']

@agent.on_query(model=SentimentRequest, replies={SentimentResponse})
async def handle_song_request(ctx: Context, sender: str, msg: SentimentRequest):
    ctx.logger.info(f'User has requested to search songs for the keyword: {msg.text}')
    english_text = await translate_to_english(msg.text)
    sentiment = await analyze_sentiment_huggingface(english_text)
    
    await ctx.send(sender, SentimentResponse(sentiment=str(sentiment)))
