import os
import json
import logging
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

logger = logging.getLogger("AuthManager")

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-alphabot-93-50")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 día

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthManager:
    def __init__(self):
        self.auth_file = "data/auth.json"
        if not os.path.exists("data"):
            os.makedirs("data")
        
        self.password_hash = self._load_password()

    def _load_password(self):
        """Carga el hash de la contraseña si existe."""
        if os.path.exists(self.auth_file):
            try:
                with open(self.auth_file, 'r') as f:
                    data = json.load(f)
                    return data.get("password_hash")
            except Exception as e:
                logger.error(f"Error al cargar auth.json: {e}")
        return None

    def is_initialized(self):
        """Verifica si ya se ha configurado una contraseña."""
        return self.password_hash is not None

    def initialize_password(self, password):
        """Configura la contraseña inicial (solo si no existe)."""
        if self.is_initialized():
            return False, "Ya existe una contraseña configurada."
        
        self.password_hash = pwd_context.hash(password)
        try:
            with open(self.auth_file, 'w') as f:
                json.dump({"password_hash": self.password_hash, "created_at": datetime.now().isoformat()}, f)
            logger.info("✅ Contraseña inicial configurada con éxito.")
            return True, "Contraseña configurada."
        except Exception as e:
            return False, str(e)

    def verify_password(self, plain_password):
        """Verifica la contraseña contra el hash."""
        if not self.password_hash:
            return False
        return pwd_context.verify(plain_password, self.password_hash)

    def create_access_token(self, data: dict):
        """Crea un token JWT."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str):
        """Verifica un token JWT."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except:
            return None
