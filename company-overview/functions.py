import os
import requests
import json

# Replace with your actual API key
API_KEY = os.getenv("AV_API_KEY")


def fetch_overview_json(ticker):
    url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={API_KEY}'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        data = response.json()
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})
    
    # Check if data is valid
    if not data or 'Symbol' not in data:
        return json.dumps({"error": "No valid data found in the response."})
    
    return data

