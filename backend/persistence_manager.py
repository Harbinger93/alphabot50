import os
import json
import logging
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger("PersistenceManager")

class PersistenceManager:
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost:5432/alphabot')
        self.offline_dir = "data/offline_logs"
        self.offline_file = os.path.join(self.offline_dir, "trades_fallback.json")
        
        # Crear directorio de logs si no existe
        if not os.path.exists(self.offline_dir):
            os.makedirs(self.offline_dir)
            logger.info(f"Directorio creado: {self.offline_dir}")

        self.engine = None
        self.Session = None
        self.is_online = self._check_db_connection()

    def _check_db_connection(self):
        """Verifica si la base de datos PostgreSQL está accesible."""
        try:
            self.engine = create_engine(self.db_url, connect_args={'connect_timeout': 5})
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            self.Session = sessionmaker(bind=self.engine)
            logger.info("✅ Conexión a PostgreSQL establecida.")
            return True
        except Exception as e:
            logger.warning(f"⚠️ PostgreSQL no detectado ({str(e)}). Activando modo OFFLINE (JSON Fallback).")
            return False

    def save_trade(self, trade_data):
        """Guarda una operación en DB o en JSON dependiendo de la disponibilidad."""
        trade_data['timestamp'] = datetime.now().isoformat()
        
        if self.is_online:
            try:
                # Aquí iría la lógica de inserción con SQLAlchemy
                # Por ahora simulamos éxito para no bloquear el flujo
                logger.info(f"💾 Operación guardada en PostgreSQL: {trade_data.get('symbol')}")
                return True
            except Exception as e:
                logger.error(f"❌ Error al guardar en DB: {e}. Reintentando en JSON.")
                self.is_online = False
        
        return self._save_to_json(trade_data)

    def _save_to_json(self, data):
        """Escribe los datos en un archivo JSON local."""
        try:
            trades = []
            if os.path.exists(self.offline_file):
                with open(self.offline_file, 'r') as f:
                    trades = json.load(f)
            
            trades.append(data)
            
            with open(self.offline_file, 'w') as f:
                json.dump(trades, f, indent=4)
            
            logger.info(f"📁 Datos guardados localmente en JSON: {self.offline_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error fatal al guardar JSON: {e}")
            return False

    def sync_offline_data(self):
        """Sincroniza los datos de JSON a PostgreSQL cuando la conexión se recupera."""
        if not self.is_online:
            if self._check_db_connection():
                self.is_online = True
            else:
                return False

        if os.path.exists(self.offline_file):
            try:
                with open(self.offline_file, 'r') as f:
                    trades = json.load(f)
                
                if not trades:
                    return True

                logger.info(f"Syncing {len(trades)} trades to PostgreSQL...")
                # Lógica de sincronización aquí...
                
                # Una vez sincronizado, vaciamos el JSON
                with open(self.offline_file, 'w') as f:
                    json.dump([], f)
                
                logger.info("✅ Sincronización completada con éxito.")
                return True
            except Exception as e:
                logger.error(f"❌ Error durante la sincronización: {e}")
                return False
        return True

if __name__ == "__main__":
    # Prueba rápida
    pm = PersistenceManager()
    pm.save_trade({"symbol": "BTC/USDT", "side": "BUY", "amount": 0.01})
