import ccxt
import os
from dotenv import load_dotenv

load_dotenv()

def test_clean_config():
    print("Iniciando prueba de Conexión de Ingeniería ALPHA-X...")
    
    # Esta configuración es IDENTICA a la de producción, 
    # solo cambian las URLs base para apuntar al entorno Demo.
    testnet_url = 'https://testnet.binancefuture.com/fapi/v1'
    
    config = {
        'apiKey': os.getenv('BINANCE_API_KEY'),
        'secret': os.getenv('BINANCE_SECRET_KEY'),
        'enableRateLimit': True,
        'options': {'defaultType': 'future'},
        'urls': {
            'api': {
                'public': testnet_url,
                'private': testnet_url,
                'fapiPublic': testnet_url,
                'fapiPrivate': testnet_url,
            }
        }
    }
    
    exchange = ccxt.binance(config)
    
    try:
        print(f"Conectando a: {testnet_url}")
        balance = exchange.fetch_balance()
        usdt_total = balance['total'].get('USDT', 0)
        print(f"CONEXION EXITOSA!")
        print(f"Saldo Detectado: ${usdt_total} USDT")
        
        if usdt_total > 0:
            print("El bot ya puede ver tu capital de prueba.")
        else:
            print("Conexión lograda, pero el balance en Testnet es 0. Revisa el Faucet de Binance.")
            
    except Exception as e:
        print(f"ERROR DE CONEXION: {e}")
        print("\nAnalizando causa raíz...")
        if "API-key format invalid" in str(e):
            print("Causa: Las llaves API no tienen el formato correcto.")
        elif "Signature for this request is not valid" in str(e):
            print("Causa: El Secret Key es incorrecto o las llaves no son para Mock Trading.")

if __name__ == "__main__":
    test_clean_config()
