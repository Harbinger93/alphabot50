import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_fetch_balance():
    print("Testing CCXT with SSL verify bypassing...")
    
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
                'fapiData': f"{demo_url}/futures/data",
                'sapi': f"{demo_url}/fapi/v1",
                'dapi': f"{demo_url}/fapi/v1",
                'v1': f"{demo_url}/fapi/v1",
                'v3': f"{demo_url}/fapi/v1",
            }
        }
    })
    
    import urllib3
    urllib3.disable_warnings() 
    # Disable SSL verification in python requests session inside CCXT
    exchange.session.verify = False
    
    try:
        balance = exchange.fetch_balance()
        print("TOTAL USDT:", balance['total'].get('USDT', 0))
        print("Success")
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    test_fetch_balance()
