# Konfiguraatio

## Yleiskuvaus
Tämä konfiguraatiodokumentti auttaa ymmärtämään RepoRouskun käyttämät konfiguraatiot, kuten Dockerin, Docker Composen ja GitLab CI/CD -putken asetukset. Näiden konfiguraatioiden avulla RepoRousku saadaan helposti käyttöön ja testaukset suoritetaan automaattisesti.

## Dockerfile-konfiguraatio

**Dockerfile**

RepoRousku on kontitettu käyttäen seuraavaa Dockerfileä, joka määrittelee ympäristön, jossa sovellus suoritetaan.

```python
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
```

**Selitys:**

* **Base Image:** Dockerfile käyttää python:3.9-slim-peruskuvaa, joka on kevyempi versio Python-kuvasta.

* **WORKDIR:** Asettaa työskentelyhakemistoksi /app.

* **COPY ja RUN:** Kopioi riippuvuustiedoston ja asentaa sovelluksen vaatimat riippuvuudet.

* **CMD:** Asettaa oletuskomennoksi Streamlit-sovelluksen suorittamisen portissa 8501.

## Docker Compose -konfiguraatio

**docker-compose.yml**

Docker Compose -tiedosto mahdollistaa sovelluksen suorittamisen Dockerilla yksinkertaisemmin määrittelemällä, miten kontit käynnistetään ja mitkä ympäristömuuttujat tarvitaan.

```python
services:
  palikka:
    build:
      context: .
      dockerfile: Dockerfile 
    ports:
      - "8501:8501"
    environment:
      GITLAB_TOKEN: "${GITLAB_TOKEN}"
```

**Selitys:**

* **services:** Määrittelee palvelun nimeltä `palikka`, joka rakentuu projektin Dockerfilen avulla.

* **ports:** Kartoitus portista 8501, jotta Streamlit-sovellus on saatavilla.

* **environment:** Ympäristömuuttuja GITLAB_TOKEN määritellään, jotta sovellus voi käyttää GitLabin APIa.