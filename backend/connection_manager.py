import ccxt
import os
import logging
from dotenv import load_dotenv

# Configuración de logging básica
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ConnectionManager")

load_dotenv()

class ConnectionManager:
    def __init__(self, exchange_id='binance'):
        self.api_key = os.getenv('BINANCE_API_KEY')
        self.secret_key = os.getenv('BINANCE_SECRET_KEY')
        # Normalizamos el valor de IS_TESTNET
        is_testnet_str = str(os.getenv('IS_TESTNET', 'True')).lower()
        self.testnet = is_testnet_str == 'true'
        
        # Inicializamos la conexión a Binance Futures (USD-M)
        self.exchange = ccxt.binanceusdm({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
                'enableDemoTrading': True # THE SECRET KEY!! Evita fugas a Spot/SAPI
            }
        })
        
        if self.testnet:
            import urllib3
            urllib3.disable_warnings()
            self.exchange.verify = False # Desactiva verificación SSL defectuosa de Demo-FAPI
            
            # Reemplazamos inteligentemente los hosts conservando las rutas de CCXT
            # Para Binance Demo Trading, necesitamos apuntar a demo-fapi específicamente
            self.exchange.urls['api']['public'] = 'https://demo-fapi.binance.com/fapi/v1'
            self.exchange.urls['api']['private'] = 'https://demo-fapi.binance.com/fapi/v1'
            self.exchange.urls['api']['fapiPrivateV3'] = 'https://demo-fapi.binance.com/fapi/v3'
            
            if 'test' in self.exchange.urls:
                self.exchange.urls['test']['public'] = 'https://demo-fapi.binance.com/fapi/v1'
                self.exchange.urls['test']['private'] = 'https://demo-fapi.binance.com/fapi/v1'
                self.exchange.urls['test']['fapiPrivateV3'] = 'https://demo-fapi.binance.com/fapi/v3'
            
            logger.info("[CONN] Aislamiento Supremo ACTIVADO (demo-fapi + SSL Bypass)")
        
        try:
            self.exchange.load_markets()
            logger.info(f"✅ Mercados cargados: {len(self.exchange.markets)} disponibles.")
        except Exception as e:
            logger.error(f"❌ Error crítico al cargar mercados: {e}")

    def get_exchange(self):
        """Devuelve la instancia activa del exchange."""
        return self.exchange

    def check_connection(self):
        """Verifica si las credenciales son válidas obteniendo el balance."""
        try:
            balance = self.exchange.fetch_balance()
            usdt_balance = balance['total'].get('USDT', 0)
            logger.info(f"✅ Conexión Exitosa. Balance disponible: {usdt_balance} USDT")
            return True
        except ccxt.AuthenticationError:
            logger.error("❌ Error de Autenticación: API Keys inválidas.")
            return False
        except ccxt.NetworkError:
            logger.error("❌ Error de Red: No se pudo contactar con el exchange.")
            return False
        except Exception as e:
            logger.error(f"❌ Error inesperado: {str(e)}")
            return False

if __name__ == "__main__":
    # Prueba de diagnóstico
    print("--- Diagnosticando AlphaBot-50 ---")
    bot_conn = ConnectionManager()
    bot_conn.check_connection()