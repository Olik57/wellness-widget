FROM python:3.10-slim

# Instalace knihoven pro Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instalace Python balíčků
RUN pip install --no-cache-dir flask requests psycopg2-binary

COPY . .

EXPOSE 8081

CMD ["python", "app.py"]
