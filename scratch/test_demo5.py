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

    # Override all API URLs intelligently!
    def override_urls(target_dict):
        for k, v in target_dict.items():
            if isinstance(v, dict):
                override_urls(v)
            elif isinstance(v, str):
                target_dict[k] = v.replace('fapi.binance.com', 'demo-fapi.binance.com')\
                                  .replace('api.binance.com', 'demo-fapi.binance.com')
                                  
    override_urls(exchange.urls['api'])

    try:
        balance = exchange.fetch_balance()
        print("TOTAL USDT:", balance['total'].get('USDT', 0))
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_balance()
