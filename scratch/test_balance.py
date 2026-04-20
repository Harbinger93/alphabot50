import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_fetch_balance():
    print("Testing CCXT balance fetch for Futures ONLY...")
    exchange = ccxt.binanceusdm({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
    })
    
    # Manual overriding of URLs for Testnet Demo Trading
    demo_url = 'https://demo-fapi.binance.com'
    exchange.urls['api']['public'] = f"{demo_url}/fapi/v1"
    exchange.urls['api']['private'] = f"{demo_url}/fapi/v1"
    exchange.urls['api']['fapiPublic'] = f"{demo_url}/fapi/v1"
    exchange.urls['api']['fapiPrivate'] = f"{demo_url}/fapi/v1"
    
    # Very important: Disable SAPI completely so it doesn't try to fetch user assets config!
    exchange.has['fetchBalance'] = True # Force it to true so it doesn't try to load SAPI options
    
    try:
        # Pass type: future to prevent spot API fallback
        balance = exchange.fetch_balance()
        print(balance)
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_balance()
