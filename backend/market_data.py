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

    def fetch_ohlcv(self, symbol, limit=50):
        """Obtiene las últimas velas de 15m de Binance para un símbolo específico."""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe=self.timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            logger.error(f"❌ Error al obtener OHLCV para {symbol}: {e}")
            return None

    def analyze_volume_anomaly(self, df, symbol):
        """Detecta anomalías de volumen usando Z-Score (2.5 Sigma)."""
        if df is None or df.empty:
            return False, 0
            
        # Tomamos los últimos 20 periodos para la media y sigma
        volume_data = df['volume'].iloc[:-1] # Excluimos la vela actual incompleta if necessary
        current_volume = df['volume'].iloc[-1]
        
        mean_vol = volume_data.mean()
        std_vol = volume_data.std()
        
        if std_vol == 0:
            return False, 0
            
        z_score = float((current_volume - mean_vol) / std_vol)
        is_anomaly = bool(z_score > 2.5)
        
        if is_anomaly:
            logger.info(f"MOVIMIENTO DE BALLENA DETECTADO en {symbol}: Z-Score={z_score:.2f} | Vol={float(current_volume)}")
            
        return is_anomaly, z_score

    def get_top_traders_sentiment(self, symbol):
        """Consulta el ratio Long/Short de Top Traders en Binance Futures para un símbolo."""
        try:
            params = {
                'symbol': symbol.replace('/', ''), 
                'period': '15m'
            }
            cache_key = f"sentiment:{symbol}"

            # En Testnet, los endpoints de fapiData (Sentiment) no suelen estar disponibles.
            if getattr(self.exchange, 'urls', {}).get('test'):
                return {
                    "ratio": 1.0,
                    "bias": "NEUTRAL (SIM)",
                    "timestamp": datetime.now().isoformat()
                }

            # Verificamos caché
            if self.redis:
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached)

            response = self.exchange.fapiDataGetTopLongShortAccountRatio(params)
            
            if not response:
                return None
                
            latest_ratio = float(response[-1]['longShortRatio'])
            
            sentiment = {
                "ratio": latest_ratio,
                "bias": "BULLISH" if latest_ratio > 1.2 else "BEARISH" if latest_ratio < 0.8 else "NEUTRAL",
                "timestamp": datetime.now().isoformat()
            }
            
            if self.redis:
                self.redis.setex(cache_key, 30, json.dumps(sentiment))
            
            return sentiment
            
        except Exception as e:
            logger.error(f"Error al obtener sentimiento para {symbol}: {e}")
            return None

    def get_market_summary(self, symbol):
        """Genera un resumen completo estructurado para un símbolo."""
        df = self.fetch_ohlcv(symbol)
        if df is None:
            return None
            
        is_whale, z_score = self.analyze_volume_anomaly(df, symbol)
        sentiment = self.get_top_traders_sentiment(symbol)
        
        return {
            "symbol": symbol,
            "price": float(df['close'].iloc[-1]) if not df.empty else 0.0,
            "indicators": {
                "vol_z_score": round(float(z_score), 2),
                "whale_signal": is_whale,
                "ls_ratio": float(sentiment['ratio']) if sentiment else 1.0
            },
            "safety": {
                "persistence_mode": "unknown",
                "cache_mode": "redis" if self.redis else "in_memory"
            }
        }
