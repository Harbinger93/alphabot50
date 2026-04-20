import asyncio
import logging
import os
from datetime import datetime
from market_data import MarketDataManager
from risk_manager import RiskManager
from persistence_manager import PersistenceManager

logger = logging.getLogger("TradingEngine")

class TradingEngine:
    def __init__(self, connection_manager):
        self.conn = connection_manager
        self.exchange = connection_manager.get_exchange()
        self.market_data = MarketDataManager(self.exchange)
        self.risk_manager = RiskManager()
        self.persistence = PersistenceManager()
        
        self.is_running = False
        self.active_position = None
        # Cargamos los símbolos desde .env
        self.symbols = os.getenv('TRADED_SYMBOLS', 'BTC/USDT').split(',')
        logger.info(f"⚙️ Configuración cargada: {len(self.symbols)} activos monitoreados.")

    async def start(self):
        """Inicia el bucle principal de trading."""
        if self.is_running:
            logger.warning("⚠️ El motor ya está corriendo.")
            return
            
        self.is_running = True
        logger.info(f"🚀 MOTOR DE TRADING ACTIVADO - Barrido de {len(self.symbols)} activos")
        
        while self.is_running:
            try:
                await self.check_all_symbols()
            except Exception as e:
                logger.error(f"❌ Error en el bucle de trading: {e}")
            
            # Esperamos 1 minuto antes de la siguiente revisión
            await asyncio.sleep(60)

    def stop(self):
        """Detiene el motor."""
        self.is_running = False
        logger.info("🛑 MOTOR DE TRADING DESACTIVADO.")

    async def check_all_symbols(self):
        """Escanea todos los símbolos configurados uno por uno."""
        if self.active_position:
            # Si hay una posición activa, no buscamos nuevas entradas
            # (Estrategia conservadora para gestión de balance)
            return

        for symbol in self.symbols:
            if not self.is_running: break
            await self.check_for_signals(symbol)
            # Pequeña pausa entre símbolos para evitar rate limits si hay muchos
            await asyncio.sleep(1)

    async def check_for_signals(self, symbol):
        """Lógica de confluencia para un símbolo específico."""
        logger.info(f"🔍 Escaneando confluencia en {symbol}...")
        
        df = self.market_data.fetch_ohlcv(symbol)
        if df is None: return

        is_whale, z_score = self.market_data.analyze_volume_anomaly(df, symbol)
        sentiment = self.market_data.get_top_traders_sentiment(symbol)
        
        if not sentiment: return

        # LOGICA DE CONFLUENCIA ALFABOT-50
        signal = None
        if is_whale:
            if sentiment['ratio'] > 1.2:
                signal = "BUY"
            elif sentiment['ratio'] < 0.8:
                signal = "SELL"
        
        if signal:
            logger.info(f"🔥 SEÑAL CONFIRMADA en {symbol}: {signal} | Z:{z_score:.2f} | R:{sentiment['ratio']}")
            await self.execute_trade(symbol, signal)
        else:
            logger.info(f"⚖️ {symbol} en equilibrio. Z:{z_score:.2f} | R:{sentiment['ratio']}")

    async def execute_trade(self, symbol, side):
        """Calcula el riesgo y lanza la orden real a Binance."""
        try:
            # 1. Obtener balance real
            balance_data = self.exchange.fetch_balance()
            free_balance = float(balance_data['free'].get('USDT', 0))
            
            # 2. Obtener precio actual
            ticker = self.exchange.fetch_ticker(symbol)
            price = float(ticker['last'])
            
            # 3. Calcular setup con RiskManager
            setup = self.risk_manager.get_trade_setup(free_balance, price, side)
            
            if setup['quantity'] <= 0:
                logger.warning(f"⚠️ {symbol}: Tamaño de posición insuficiente.")
                return

            logger.info(f"📦 Preparando orden: {side} {setup['quantity']} {symbol} @ {price}")
            
            # 4. Ejecutar orden de mercado
            order = self.exchange.create_order(
                symbol=symbol,
                type='market',
                side=side.lower(),
                amount=setup['quantity']
            )
            
            # 5. Colocar SL y TP
            self.exchange.create_order(
                symbol=symbol,
                type='stop_market',
                side='sell' if side == 'BUY' else 'buy',
                amount=setup['quantity'],
                params={'stopPrice': setup['sl']}
            )
            
            self.exchange.create_order(
                symbol=symbol,
                type='take_profit_market',
                side='sell' if side == 'BUY' else 'buy',
                amount=setup['quantity'],
                params={'stopPrice': setup['tp']}
            )
            
            self.active_position = {**setup, "symbol": symbol}
            logger.info(f"✅ OPERACIÓN ABIERTA en {symbol}: ID {order['id']}")
            
            # 6. Persistencia
            self.persistence.log_trade({
                "id": order['id'],
                "timestamp": datetime.now().isoformat(),
                "symbol": symbol,
                "side": side,
                "qty": setup['quantity'],
                "entry": price,
                "sl": setup['sl'],
                "tp": setup['tp']
            })
            
        except Exception as e:
            logger.error(f"❌ Error crítico en trade ({symbol}): {e}")
