import asyncio
import logging
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
        self.symbol = 'BTC/USDT'

    async def start(self):
        """Inicia el bucle principal de trading."""
        if self.is_running:
            logger.warning("⚠️ El motor ya está corriendo.")
            return
            
        self.is_running = True
        logger.info(f"🚀 MOTOR DE TRADING ACTIVADO - Monitoreando {self.symbol}")
        
        while self.is_running:
            try:
                await self.check_for_signals()
            except Exception as e:
                logger.error(f"❌ Error en el bucle de trading: {e}")
            
            # Esperamos 1 minuto antes de la siguiente revisión (ajustable)
            await asyncio.sleep(60)

    def stop(self):
        """Detiene el motor."""
        self.is_running = False
        logger.info("🛑 MOTOR DE TRADING DESACTIVADO.")

    async def check_for_signals(self):
        """Lógica de confluencia para abrir operaciones."""
        if self.active_position:
            # Por ahora el bot solo maneja una posición a la vez
            # Aquí se podría añadir lógica para monitorear el cierre manual o por SL/TP
            return

        logger.info(f"🔍 Escaneando confluencia en {self.symbol}...")
        
        df = self.market_data.fetch_ohlcv()
        is_whale, z_score = self.market_data.analyze_volume_anomaly(df)
        sentiment = self.market_data.get_top_traders_sentiment()
        
        if not sentiment:
            return

        # LOGICA DE CONFLUENCIA ALFABOT-50
        # 1. Anomalía de Volumen (Z-Score > 2.5)
        # 2. Sentimiento a favor (Ratio > 1.2 para Buy, < 0.8 para Sell)
        
        signal = None
        if is_whale:
            if sentiment['ratio'] > 1.2:
                signal = "BUY"
            elif sentiment['ratio'] < 0.8:
                signal = "SELL"
        
        if signal:
            logger.info(f"🔥 SEÑAL CONFIRMADA: {signal} | Z-Score: {z_score:.2f} | Ratio: {sentiment['ratio']}")
            await self.execute_trade(signal)
        else:
            logger.info(f"⚖️ Mercado en equilibrio. Z:{z_score:.2f} | R:{sentiment['ratio']}")

    async def execute_trade(self, side):
        """Calcula el riesgo y lanza la orden real a Binance."""
        try:
            # 1. Obtener balance real
            balance_data = self.exchange.fetch_balance()
            free_balance = float(balance_data['free'].get('USDT', 0))
            
            # 2. Obtener precio actual
            ticker = self.exchange.fetch_ticker(self.symbol)
            price = float(ticker['last'])
            
            # 3. Calcular setup con RiskManager
            setup = self.risk_manager.get_trade_setup(free_balance, price, side)
            
            if setup['quantity'] <= 0:
                logger.warning("⚠️ Tamaño de posición insuficiente para los parámetros de riesgo.")
                return

            logger.info(f"📦 Preparando orden: {side} {setup['quantity']} BTC @ {price}")
            
            # 4. Ejecutar orden de mercado
            # Nota: En Testnet esto se reflejará inmediatamente
            order = self.exchange.create_order(
                symbol=self.symbol,
                type='market',
                side=side.lower(),
                amount=setup['quantity']
            )
            
            # 5. Colocar SL y TP (Órdenes automáticas)
            # En producción esto debería ser más robusto (órdenes ligadas)
            self.exchange.create_order(
                symbol=self.symbol,
                type='stop_market',
                side='sell' if side == 'BUY' else 'buy',
                amount=setup['quantity'],
                params={'stopPrice': setup['sl']}
            )
            
            self.exchange.create_order(
                symbol=self.symbol,
                type='take_profit_market',
                side='sell' if side == 'BUY' else 'buy',
                amount=setup['quantity'],
                params={'stopPrice': setup['tp']}
            )
            
            self.active_position = setup
            logger.info(f"✅ OPERACIÓN ABIERTA: ID {order['id']}")
            
            # 6. Persistencia
            self.persistence.log_trade({
                "id": order['id'],
                "timestamp": datetime.now().isoformat(),
                "symbol": self.symbol,
                "side": side,
                "qty": setup['quantity'],
                "entry": price,
                "sl": setup['sl'],
                "tp": setup['tp']
            })
            
        except Exception as e:
            logger.error(f"❌ Error crítico al ejecutar trade: {e}")

if __name__ == "__main__":
    from connection_manager import ConnectionManager
    
    async def test_engine():
        conn = ConnectionManager()
        engine = TradingEngine(conn)
        await engine.start()

    asyncio.run(test_engine())
