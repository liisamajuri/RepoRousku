# Virallinen Python 3.9 -image
FROM python:3.9-slim

# Aseta työhakemisto
WORKDIR /app

# Kopioi requirements.txt juurikansiosta konttiin
COPY requirements.txt .

# Asenna riippuvuudet
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi kaikki tiedostot src-kansiosta konttiin
COPY src /app/src

# Aseta oletuskomento, joka suorittaa Streamlit-sovelluksen
CMD ["streamlit", "run", "src/app.py", "--server.port=8501", "--server.enableCORS=false"]