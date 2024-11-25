# Python 3.9 -image
FROM python:3.9-slim

# Aseta työhakemisto
WORKDIR /app

# Kopioi requirements.txt juurikansiosta konttiin
COPY requirements.txt .

# Asenna riippuvuudet
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi lähdekoodi
COPY src /app/src
COPY tests /app/tests
COPY api /app/api

# Kopioi dokumentaatiotiedostot
COPY mkdocs.yml .
COPY docs /app/docs

# Käynnistä API (jos tätä Dockerfile käytetään suoraan)
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8088"]