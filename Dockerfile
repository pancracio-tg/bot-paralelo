# Imagen base
FROM python:3.13-slim

WORKDIR /app

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install mysql-connector-python

# Copiar código
COPY . .

# Configuraciones Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Comando por defecto
CMD ["python", "bot.py"]
