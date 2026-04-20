from fastapi import FastAPI, HTTPException
from connection_manager import ConnectionManager
from market_data import MarketDataManager
from risk_manager import RiskManager
from persistence_manager import PersistenceManager
from auth_manager import AuthManager
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
    auth_manager = AuthManager()
except Exception as e:
    print(f"⚠️ Error al inicializar módulos: {e}")

@app.get("/")
async def root():
    return {
        "message": "AlphaBot-50 API is running", 
        "status": "online",
        "initialized": auth_manager.is_initialized()
    }

@app.post("/auth/init")
async def init_auth(req: LoginRequest):
    """Configura la contraseña inicial."""
    success, msg = auth_manager.initialize_password(req.password)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"message": "Contraseña configurada con éxito"}

@app.post("/auth/login")
async def login(req: LoginRequest):
    """Valida la contraseña y retorna un token JWT."""
    if not auth_manager.verify_password(req.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    token = auth_manager.create_access_token({"sub": "admin"})
    return {"access_token": token, "token_type": "bearer"}

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
        return {"total_usdt": balance['total'].get('USDT', 0), "free_usdt": balance['free'].get('USDT', 0)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sync")
async def sync_data():
    """Fuerza la sincronización de datos locales a PostgreSQL."""
    success = persistence_manager.sync_offline_data()
    return {"synced": success, "db_online": persistence_manager.is_online}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
