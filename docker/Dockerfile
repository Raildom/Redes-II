FROM python:3.9-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY src/ ./src/
COPY requisitos.txt .

# Instala dependências Python
RUN pip install -r requisitos.txt

# Expõe a porta do servidor
EXPOSE 8080

# Comando padrão (pode ser sobrescrito)
CMD ["python", "src/configuracao.py"]
