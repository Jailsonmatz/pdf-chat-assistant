# Use uma imagem Python leve
FROM python:3.9-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Copia o arquivo requirements.txt da UI para o container
COPY requirements.txt .

# Instala as dependências da UI
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código da UI para o container
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Define o comando padrão para iniciar o Streamlit
CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
