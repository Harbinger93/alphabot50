import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_fetch_balance():
    print("Testing CCXT with enableDemoTrading...")
    exchange = ccxt.binanceusdm({
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future',
            'enableDemoTrading': True # THE SECRET KEY!!
        }
    })
    
    # Enable explicit Testnet flag
    exchange.set_sandbox_mode(True)
    
    try:
        balance = exchange.fetch_balance()
        print(balance['total'])
        print("Success")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_fetch_balance()
