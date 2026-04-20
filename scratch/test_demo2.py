import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_fetch_balance():
    print("Testing CCXT with enableDemoTrading and manual URLs...")
    
    demo_url = 'https://demo-fapi.binance.com'
    exchange = ccxt.binanceusdm({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'enableDemoTrading': True
        },
        'urls': {
            'api': {
                'public': f"{demo_url}/fapi/v1",
                'private': f"{demo_url}/fapi/v1",
                'fapiPublic': f"{demo_url}/fapi/v1",
                'fapiPrivate': f"{demo_url}/fapi/v1",
            }
        }
    })
    
    balance = exchange.fetch_balance()
    print("TOTAL:", balance['total'])
    print("Success")


if __name__ == "__main__":
    test_fetch_balance()
