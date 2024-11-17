# Python 3.9 -image
FROM python:3.9-slim

# Aseta työhakemisto
WORKDIR /app

# Kopioi requirements.txt juurikansiosta konttiin
COPY requirements.txt .

# Asenna riippuvuudet
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi src-kansiot
COPY src /app/src
COPY tests /app/tests

# TODO: docs