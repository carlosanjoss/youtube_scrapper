FROM python:3.11-slim

WORKDIR /app

# instala dependências primeiro (camada cacheável)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copia o código
COPY . .

# cria usuário sem privilégios de root
RUN useradd -m scraper && chown -R scraper:scraper /app
USER scraper

# garante que as pastas de saída existam
RUN mkdir -p data/channels logs

CMD ["python", "main.py"]
