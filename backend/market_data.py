import pandas as pd
import numpy as np
import logging
import redis
import json
from datetime import datetime

logger = logging.getLogger("MarketDataManager")

class MarketDataManager:
    def __init__(self, exchange, redis_host='localhost', redis_port=6379):
        self.exchange = exchange
        self.symbol = 'BTC/USDT'
        self.timeframe = '15m'
        
        # Conexión a Redis con Fallback a memoria local
        try:
            self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
            self.redis.ping()
            logger.info("✅ Conexión a Redis exitosa.")
        except Exception as e:
            logger.warning(f"⚠️ Redis no disponible: {e}. Usando caché en memoria.")
            self.redis = None
            self.local_cache = {}

    def fetch_ohlcv(self, limit=50):
        """Obtiene las últimas velas de 15m de Binance."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"❌ Error al obtener OHLCV: {e}")
            return None

    def analyze_volume_anomaly(self, df):
        """Detecta anomalías de volumen usando Z-Score (2.5 Sigma)."""
        if df is None or df.empty:
            return False, 0
            
        # Tomamos los últimos 20 periodos para la media y sigma
        volume_data = df['volume'].iloc[:-1] # Excluimos la vela actual incompleta si es necesario
        current_volume = df['volume'].iloc[-1]
        
        mean_vol = volume_data.mean()
        std_vol = volume_data.std()
        
        if std_vol == 0:
            return False, 0
            
        z_score = (current_volume - mean_vol) / std_vol
        is_anomaly = z_score > 2.5
        
        if is_anomaly:
            logger.info(f"🚨 MOVIMIENTO DE BALLENA DETECTADO: Z-Score={z_score:.2f} | Vol={current_volume}")
            
        return is_anomaly, z_score

    def get_top_traders_sentiment(self):
        """Consulta el ratio Long/Short de Top Traders en Binance Futures."""
        try:
            # Usamos el API implícito de CCXT para el endpoint de Binance
            # GET /futures/data/topLongShortAccountRatio
            params = {
                'symbol': self.symbol.replace('/', ''),
                'period': '15m'
            }
            
            # Verificamos si hay caché en Redis
            cache_key = f"sentiment:{self.symbol}"
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

            response = self.exchange.fapiPublicGetTopLongShortAccountRatio(params)
            
            if not response:
                return None
                
            latest_ratio = float(response[-1]['longShortRatio'])
            
            # Formateamos el resultado
            sentiment = {
                "ratio": latest_ratio,
                "bias": "BULLISH" if latest_ratio > 1.2 else "BEARISH" if latest_ratio < 0.8 else "NEUTRAL",
                "timestamp": datetime.now().isoformat()
            }
            
            # Guardamos en caché por 30 segundos
            if self.redis:
                self.redis.setex(cache_key, 30, json.dumps(sentiment))
            
            return sentiment
            
        except Exception as e:
            logger.error(f"❌ Error al obtener sentimiento: {e}")
            return None

    def get_market_summary(self):
        """Genera un resumen completo para el trigger del bot."""
        df = self.fetch_ohlcv()
        is_whale, z_score = self.analyze_volume_anomaly(df)
        sentiment = self.get_top_traders_sentiment()
        
        return {
            "symbol": self.symbol,
            "price": df['close'].iloc[-1] if df is not None else None,
            "whale_movement": is_whale,
            "volume_z_score": z_score,
            "sentiment": sentiment,
            "ready_to_trade": is_whale and sentiment and sentiment['bias'] != "NEUTRAL"
        }

if __name__ == "__main__":
    from connection_manager import ConnectionManager
    
    conn = ConnectionManager()
    mdm = MarketDataManager(conn.get_exchange())
    
    print("--- Analizando BTC/USDT ---")
    summary = mdm.get_market_summary()
    print(json.dumps(summary, indent=4))
