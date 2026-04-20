import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_sentiment_api():
    print("Testing Binance Sentiment API methods...")
    exchange = ccxt.binance({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
        'options': {'defaultType': 'future'}
    })
    exchange.set_sandbox_mode(True)
    
    params = {'symbol': 'BTCUSDT', 'period': '15m'}
    
    methods_to_try = [
        'fapiDataGetTopLongShortAccountRatio',
        'fapiPublicGetTopLongShortAccountRatio',
        'futuresGetDataTopLongShortAccountRatio'
    ]
    
    for method in methods_to_try:
        try:
            print(f"Trying {method}...")
            if hasattr(exchange, method):
                func = getattr(exchange, method)
                res = func(params)
                print(f"✅ Success with {method}: {len(res)} items found.")
                return method
            else:
                print(f"❌ {method} not found in exchange object.")
        except Exception as e:
            print(f"⚠️ Error with {method}: {e}")
            
    return None

if __name__ == "__main__":
    test_sentiment_api()
