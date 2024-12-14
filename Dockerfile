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

# Kopioi tyylitiedosto
COPY .streamlit/config.toml /app/.streamlit/config.toml

# Kopioi tarvittavat tiedotot .rest-tiedostojen autodokumentaatiota varten
COPY requests /app/requests
COPY generate_rest_docs.py ./generate_rest_docs.py

# Muodosta .rest-tiedostoista markdown-tiedosto MkDocsia varten
RUN python generate_rest_docs.py


# Käynnistä API (jos tätä Dockerfile käytetään suoraan)
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8088"]