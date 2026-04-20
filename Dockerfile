# --- BACKEND BUILD ---
FROM python:3.11-slim

WORKDIR /app

# Instalamos dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del backend
COPY backend/ ./backend/
COPY .env .

# Exponemos el puerto de FastAPI
EXPOSE 8000

# Iniciamos el servidor
CMD ["python", "backend/main.py"]
