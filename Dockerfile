
FROM python:3.10-slim

WORKDIR /app

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . .

# Expõe a porta
EXPOSE 8000

# Inicia a aplicação
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
