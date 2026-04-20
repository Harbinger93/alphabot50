import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_fetch_balance():
    demo_url = 'https://demo-fapi.binance.com'
    exchange = ccxt.binanceusdm({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'enableDemoTrading': True 
        }
    })
    
    import urllib3
    urllib3.disable_warnings() 
    exchange.verify = False 

    # Override all API URLs safely
    base_demo = f"{demo_url}/fapi/v1"
    for key in list(exchange.urls['api'].keys()):
        exchange.urls['api'][key] = base_demo
        
    exchange.urls['api']['fapiData'] = f"{demo_url}/futures/data"

    try:
        balance = exchange.fetch_balance()
        print("TOTAL USDT:", balance['total'].get('USDT', 0))
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_balance()
