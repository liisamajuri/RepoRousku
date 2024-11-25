# Konfiguraatio

## Yleiskuvaus
Tämä dokumentti esittelee RepoRouskun tärkeimmät konfiguraatiotiedostot, kuten:
* **Dockerfile**
* **Docker Compose -konfiguraatio**
* **GitLab CI/CD -putken määrittely**
* **MkDocs-dokumentaation konfiguraatio**

Näiden konfiguraatioiden avulla sovellus voidaan asentaa, testata, käyttää ja dokumentoida tehokkaasti.

## Dockerfile

Dockerfile määrittää ympäristön, jossa RepoRousku-sovellus suoritetaan.

```dockerfile
# Python 3.9 -image
FROM python:3.9-slim

# Aseta työhakemisto
WORKDIR /app

# Kopioi riippuvuudet
COPY requirements.txt .

# Asenna riippuvuudet
RUN pip install --no-cache-dir -r requirements.txt

# Kopioi lähdekoodi ja dokumentaatio
COPY src /app/src
COPY tests /app/tests
COPY api /app/api
COPY mkdocs.yml .
COPY docs /app/docs

# Oletuskomento (API:n käynnistys)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8088"]

```

**Selitys:**

* **Base image**: Kevyt Python 3.9 -kuva (slim).
**Riippuvuuksien hallinta**: Pip-asennus requirements.txt-tiedostosta.
**Lähdekoodi**: Sisältää lähdekoodin, testit, dokumentaation ja API:n.
**Oletuskomento**: Käynnistää API:n Uvicorn-palvelimella.

## Docker Compose -konfiguraatio

docker-compose.yml määrittää sovelluksen eri palvelut.

```yaml
services:
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"
    environment:
      GITLAB_TOKEN: "${GITLAB_TOKEN}"
      PYTHONPATH: "/app/src"
    volumes:
      - ./tests/reports:/app/tests/reports
    command: >
      sh -c "
      pip install -r requirements.txt &&
      streamlit run src/app.py --server.port=8501 --server.enableCORS=false"

```

**Palvelut:**

* **streamlit**: Käynnistää RepoRouskun Streamlit-sovelluksen portissa 8501.
* **reports**: Tarjoaa testiraportit HTTP-palvelimella.
* **docs**: Käynnistää MkDocs-dokumentaation palvelimella portissa 8502.
* **api**: Käynnistää API:n Uvicorn-palvelimella portissa 8088.

## GitLab CI/CD

GitLab CI/CD -putki sisältää neljä vaihetta:

1. Lint
2. Test
3. Coverage
4. Docs

```yaml
stages:
  - lint
  - test
  - coverage
  - docs

lint:
  stage: lint
  script:
    - ruff check src -v
test:
  stage: test
  script:
    - coverage run -m pytest -v
coverage:
  stage: coverage
  script:
    - coverage report -m
    - coverage html -d tests/reports/coverage_html
docs:
  stage: docs
  script:
    - mkdocs build
```

**Selitys:**
1. Lint: Tarkistaa koodin laadun Ruffin avulla.
2. Test: Suorittaa yksikkö-, API- ja integraatiotestit Pytestillä.
3. Coverage: Generoi koodikattavuusraportin.
4. Docs: Rakentaa dokumentaation MkDocsilla.

## MkDocs-konfiguraatio

MkDocs luo staattisen sivuston sovelluksen dokumentaatiosta.

```yaml
site_name: RepoRouskun koodidokumentaatio ja käyttöohjeet
theme:
  name: material
  palette:
    primary: black
    accent: deep orange
nav:
  - Tervehdys: index.md
  - Käyttöohjeet: usage.md
  - Koodidokumentaatio: modules_api_reference.md
  - Konfiguraatioista: configuration.md
plugins:
  - search
  - mkdocstrings:
      handlers:
        python:
          rendering:
            show_root_toc_entry: false
```

**Selitys:**
* **Teema:** Material Design (slate-värimaailma).
* **Navigaatio:** Sivut esitetään järjestyksessä nav-osassa.
* **Plugins:** Hakutoiminnallisuus ja automaattisesti generoitu Python-koodidokumentaatio.