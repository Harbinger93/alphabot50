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
        
        # Inicializamos la conexión a Binance Futures
        self.exchange = getattr(ccxt, exchange_id)({
            'apiKey': self.api_key,
            'secret': self.secret_key,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future'  # Obligatorio para perpetuos
            }
        })
        
        if self.testnet:
            self.exchange.set_sandbox_mode(True)
            logger.info("[CONN] Modo Sandbox (Testnet) ACTIVADO.")

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