from fastapi import FastAPI, HTTPException
from connection_manager import ConnectionManager
from market_data import MarketDataManager
from risk_manager import RiskManager
from persistence_manager import PersistenceManager
from trading_engine import TradingEngine
import asyncio
from persistence_manager import PersistenceManager
from pydantic import BaseModel
import uvicorn

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AlphaBot-50 Backend API")

# Configurar CORS para permitir comunicación con el Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se limitaría a la URL del Dashboard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class LoginRequest(BaseModel):
    password: str

# Inicialización de módulos
try:
    conn_manager = ConnectionManager()
    market_manager = MarketDataManager(conn_manager.get_exchange())
    risk_manager = RiskManager()
    persistence_manager = PersistenceManager()
    trading_engine = TradingEngine(conn_manager)
except Exception as e:
    print(f"⚠️ Error al inicializar módulos: {e}")

@app.get("/")
async def root():
    return {
        "message": "AlphaBot-50 API is running", 
        "status": "online",
        "initialized": True
    }

@app.get("/health")
async def health_check():
    """Verifica la salud del sistema y la conexión con el exchange."""
    is_connected = conn_manager.check_connection()
    return {
        "status": "ok" if is_connected else "error",
        "exchange_connected": is_connected,
        "timestamp": asyncio.get_event_loop().time()
    }

@app.get("/market-status")
async def get_market_status():
    """Retorna el estado del mercado estructurado para el Dashboard."""
    try:
        summary = market_manager.get_market_summary()
        
        # Inyectamos el estado real de la persistencia
        summary["safety"]["persistence_mode"] = "postgresql" if persistence_manager.is_online else "fallback_json"
        
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/balance")
async def get_balance():
    """Consulta el balance actual de la cuenta en Binance Futures."""
    try:
        exchange = conn_manager.get_exchange()
        balance = exchange.fetch_balance()
        return {
            "total_usdt": float(balance['total'].get('USDT', 0)), 
            "free_usdt": float(balance['free'].get('USDT', 0))
        }
    except Exception as e:
        print(f"❌ Error en /balance: {e}")
        return {"total_usdt": 0.0, "free_usdt": 0.0, "error": str(e)}

@app.get("/sync")
async def sync_data():
    """Fuerza la sincronización de datos locales a PostgreSQL."""
    success = persistence_manager.sync_offline_data()
    return {"synced": success, "db_online": persistence_manager.is_online}

@app.get("/bot/status")
async def get_bot_status():
    return {"running": trading_engine.is_running, "active_position": trading_engine.active_position}

@app.post("/bot/start")
async def start_bot():
    if not trading_engine.is_running:
        asyncio.create_task(trading_engine.start())
        return {"message": "Bot iniciado"}
    return {"message": "El bot ya está corriendo"}

@app.post("/bot/stop")
async def stop_bot():
    trading_engine.stop()
    return {"message": "Bot detenido"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
