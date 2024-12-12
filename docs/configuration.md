# Konfiguraatio

## Yleiskuvaus
Tämä dokumentti esittelee RepoRouskun tärkeimmät konfiguraatiotiedostot, kuten:

* **Dockerfile**
* **Docker Compose -konfiguraatio**
* **GitLab CI/CD -putken määrittely**
* **MkDocs-dokumentaation konfiguraatio**

Näiden konfiguraatioiden avulla sovellus voidaan asentaa, testata, deployata, käyttää ja dokumentoida tehokkaasti.

## Dockerfile

Dockerfile määrittää ympäristön, jossa RepoRousku-sovellus suoritetaan.

```dockerfile
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

# Kopioi tarvittavat tiedotot .rest-tiedostojen autodokumentaatiota varten
COPY requests /app/requests
COPY generate_rest_docs.py ./generate_rest_docs.py

# Muodosta .rest-tiedostoista markdown-tiedosto MkDocsia varten
RUN python generate_rest_docs.py


# Käynnistä API (jos tätä Dockerfile käytetään suoraan)
# CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8088"]

```

**Selitys:**

* **Base image**: Kevyt Python 3.9 -kuva (slim).

* **Riippuvuuksien hallinta**: Asennetaan Python-riippuvuudet requirements.txt-tiedostosta käyttämällä pip-paketinhallintaa. Optio --no-cache-dir poistaa asennusvälimuistin, mikä pienentää kuvan kokoa

* **Lähdekoodi**: Kopioi src, tests, docs ja api-kansiot projektista konttiin hakemistoon /app. Kopioi myös requests-hakemiston ja generate_rest_docs.py-skriptin konttiin. Nämä käytetään REST-rajapintojen dokumentoimiseen.

* **Oletuskomento**: Käynnistää API:n Uvicorn-palvelimella.


## Docker Compose -konfiguraatio

`docker-compose.yml`, `docker-compose.dev.yml` ja `docker-compose.prod.yml` määrittävät sovelluksen eri käytto/kehitysvaiheiden docker-kontit. 


### `docker-compose.dev.yml`

```yml
services:
  streamlit:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8501:8501"  # Streamlit-portti
    environment:
      GITLAB_TOKEN: "${GITLAB_TOKEN}"
      PYTHONPATH: "/app/src"
    volumes:
      - ./tests/reports:/app/tests/reports
      - ./.env:/app/.env
      - ./.streamlit:/app/.streamlit
    command: >
      sh -c "
      pip install -r requirements.txt &&
      echo '***************************************************************************************************************************************************************' &&
      echo 'PALIKKAPALVELUT-SOVELLUS SAATAVILLA: http://localhost:8501' &&
      echo '***************************************************************************************************************************************************************' &&
      streamlit run src/app.py --server.port=8501 --server.enableCORS=false 
      "

  tests:
    build:
      context: .
      dockerfile: Dockerfile
    env_file:
      - .env
    environment:
      GITLAB_TOKEN: "${GITLAB_TOKEN}"
      CLOCKIFY_TOKEN: "${CLOCKIFY_TOKEN}"
      PYTHONPATH: "/app/src"
    volumes:
      - ./tests:/app/tests
      - ./tests/reports:/app/tests/reports
      - ./.env:/app/.env
    command: >
      sh -c "
      echo '***************************************************************************************************************************************************************' &&
      ruff check src -v &&
      echo '***************************************************************************************************************************************************************' &&
      coverage run -m pytest -v --tb=short --html=tests/reports/unit_test_report.html --self-contained-html tests/unit_tests.py &&
      echo '***************************************************************************************************************************************************************' &&
      coverage run -m pytest -v --tb=short --html=tests/reports/api_test_report.html --self-contained-html tests/api_tests.py &&
      echo '***************************************************************************************************************************************************************' &&
      coverage run -m pytest -v --tb=short --html=tests/reports/integration_test_report.html --self-contained-html tests/integration_tests.py &&
      echo '***************************************************************************************************************************************************************' &&
      coverage report -m &&
      coverage html -d tests/reports/coverage_html &&
      echo '***************************************************************************************************************************************************************' &&
      echo 'TESTIRAPORTIT SAATAVILLA: http://localhost:8010' &&
      echo '***************************************************************************************************************************************************************'
      "

  reports:
    image: python:3.9-slim
    command: >
      sh -c "
      echo '***************************************************************************************************************************************************************' &&
      echo 'YKSIKKÖTESTIRAPORTTI SAATAVILLA: http://localhost:8010/unit_test_report.html' &&
      echo 'API-TESTIRAPORTTI SAATAVILLA: http://localhost:8010/api_test_report.html' &&
      echo 'INTEGRAATIOTESTIRAPORTTI SAATAVILLA: http://localhost:8010/integration_test_report.html' &&
      echo 'TESTIEN KATTAVUUSRAPORTTI SAATAVILLA: http://localhost:8010/coverage_html/index.html' &&
      echo '***************************************************************************************************************************************************************' &&
      python3 -m http.server 8010 -d /app/tests/reports
      "
    volumes:
      - ./tests/reports:/app/tests/reports
    ports:
      - "8010:8010"  # Testiraporttien portti

  docs:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8502:8502"  # MkDocs-dokumentaation portti
    command: >
      sh -c "
      echo '***************************************************************************************************************************************************************' &&
      echo 'PROJEKTIDOKUMENTAATIO SAATAVILLA: http://localhost:8502' &&
      echo '***************************************************************************************************************************************************************' &&
      mkdocs serve -a 0.0.0.0:8502
      "

  api:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8088:8088"  # API:n ulkoinen portti
    environment:
      PYTHONPATH: "/app/src:/app/api"
    env_file:
      - .env
    volumes:
      - ./api:/app/api
      - ./src:/app/src
    command: >
      sh -c "
      pip install -r requirements.txt &&
      echo '***************************************************************************************************************************************************************' &&
      echo 'API-RAJAPINTA SAATAVILLA: http://localhost:8088' &&
      echo 'API-DOKUMENTAATIO SAATAVILLA: http://localhost:8088/docs' &&
      echo '***************************************************************************************************************************************************************' &&
      uvicorn api.main:app --host 0.0.0.0 --port 8088
      "
```



**Tarkoitus:**

Tämä on erityisesti kehitysympäristöön suunnattu versio, joka sisältää laajempia konfiguraatioita ja useita palveluita.

**Keskeiset ominaisuudet:**

Palveluita on useita: 

* streamlit
* tests 
* reports
* docs
* api

**Streamlit-palvelu:** Käynnistää sovelluksen ja tulostaa hyödyllistä tietoa konsoliin, kuten käyttölinkit.

**Tests-palvelu:** Käyttää testien ajamiseen ja testiraporttien generoimiseen Python-työkaluilla, kuten pytest ja coverage. Raportit tallennetaan volyymiin.

**Reports-palvelu:** Käynnistää palvelimen, joka isännöi testiraportteja portissa 8010.

**Docs-palvelu:** Käynnistää MkDocs-palvelimen dokumentaatiota varten portissa 8502.

**API-palvelu:** Käynnistää API:n uvicorn-palvelimella portissa 8088.


## GitLab CI/CD

Pipelines koostuu useista vaiheista, jotka suoritetaan järjestyksessä:

1. Linttaus (koodin tarkistaminen tyyli- ja syntaksivirheiden varalta).
2. Testit (automaattiset testit).
3. Kattavuus (raportoi testien kattavuuden).
4. Dokumentaatio (MkDocs-dokumentaation generointi).
5. Tuotantoversion rakentaminen.
6. Tuotantoversion käyttöönotto.

```yaml
# Oletuskuva ja palvelut
default:
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind # Docker-in-Docker -palvelu, jotta voidaan suorittaa Docker-käskyjä

# Pipelinessä käytettävät vaiheet
stages:
  - lint
  - test
  - coverage
  - docs
  - build-prod
  - deploy-prod

# Pipelinessä käytettävät muuttujat
variables:
  PYTHONPATH: "$CI_PROJECT_DIR/src" # Python-moduulien hakupolku
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip" # Pipin välimuistin sijainti

# Cache-asetukset (välimuistin sijainnit)
cache:
  paths:
    - .cache/pip
    - .pytest_cache
    - __pycache__

# Oletusskriptit, joita ajetaan ennen varsinaisia vaiheita
.default_settings:
  before_script:
    - python --version
    - pip install --no-cache-dir -r requirements.txt
    - mkdir -p tests/reports
    - mkdir -p tests/artefacts
    - export PYTHONPATH=$CI_PROJECT_DIR/src

# Linttausvaihe: tarkistaa koodin tyyli-/syntaksivirheet
lint:
  stage: lint
  image: python:3.9-slim
  extends: .default_settings
  tags:
    - docker
  allow_failure: true # Virheet linttausvaiheessa eivät estä pipelinea etenemästä
  script:
    - ruff check src -v # Suorittaa Ruff-linttausohjelman   

# Testausvaihe: suorittaa testit ja generoi testiraportit    
test:
  stage: test
  image: python:3.9-slim
  extends: .default_settings
  tags:
    - docker
  allow_failure: false # Pipeline epäonnistuu, jos testit epäonnistuvat  
  script:
    - coverage run -m pytest -v # Suorittaa testit ja mittaa testien kattavuutta
  variables:
    CLOCKIFY_TOKEN: $CLOCKIFY_TOKEN
    GITLAB_TOKEN: $GITLAB_TOKEN
  artifacts: # Tiedostot, jotka säilytetään vaiheen jälkeen
    paths:
      - .coverage
      - tests/reports/*.html
      - tests/artefacts/
    expire_in: 1 week # Artefact-tiedostojen säilytysaika

# Kattavuusraportin vaihe: tulostaa ja generoi kattavuusraportin
coverage:
  stage: coverage
  image: python:3.9-slim
  extends: .default_settings
  tags:
    - docker
  allow_failure: true # Pipeline ei epäonnistu kattavuusraportin epäonnistumisesta  
  script:
    - if [ -f .coverage ]; then coverage report -m; fi
    - if [ -f .coverage ]; then coverage html -d tests/reports/coverage_html; fi
  artifacts: # Tiedostot, jotka säilytetään vaiheen jälkeen
    paths:
      - tests/reports/coverage_html/
    expire_in: 1 week # Artefact-tiedostojen säilytysaika

# Dokumentaation rakentaminen MkDocsilla
docs:
  stage: docs
  image: python:3.9-slim
  extends: .default_settings
  tags:
    - docker
  script:
    - mkdocs build # Rakentaa dokumentaation
  artifacts: # Tiedostot, jotka säilytetään vaiheen jälkeen
    paths:
      - site/ # Valmiin dokumentaation sijainti
    expire_in: 1 week # Artefact-tiedostojen säilytysaika
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"' # Rakennetaan vain main-branchista

# Tuotantoversion Docker-imagen rakentaminen
build-prod:
  stage: build-prod
  image: docker:24.0.5
  services:
    - docker:24.0.5-dind
  tags:
    - dind # Käytetään Docker-in-Docker-ympäristöä
  environment: production # Asettaa ympäristön tuotantoympäristöksi
  before_script:
    - docker info # Tulostaa Dockerin tiedot
    - echo "$CI_REGISTRY_PASSWORD" | docker login $CI_REGISTRY -u $CI_REGISTRY_USER --password-stdin # Kirjautuu Docker-rekisteriin
  script:
    - docker compose build --no-cache --push
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"' # Rakennetaan vain main-branchista

# Tuotantoversion käyttöönottaminen
deploy-prod:
  stage: deploy-prod
  when: manual # Käynnistetään manuaalisesti
  tags:
    - shell # Käyttää Shell-tagiin liitettyä runneria
  environment: production # Asettaa ympäristön tuotantoympäristöksi
  script:
    - 'command -v ssh-agent >/dev/null || ( apk add --update openssh )' # Varmistaa, että SSH-agent on asennettu
    - eval $(ssh-agent -s) # Käynnistää SSH-agentin
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add - # Lisää yksityisen SSH-avaimen
    - mkdir -p ~/.ssh # Luo .ssh-hakemiston
    - chmod 700 ~/.ssh
    - ssh-keyscan $DEPLOYMENT_SERVER >> ~/.ssh/known_hosts # Lisää palvelimen avaimet known_hosts-tiedostoon
    - chmod 644 ~/.ssh/known_hosts
    - scp docker-compose.prod.yml $SSH_USER@$DEPLOYMENT_SERVER:~/code/microservices/palikkapalvelut # Kopioi Docker-compose.prod-tiedoston palvelimelle
    - |
      ssh $SSH_USER@$DEPLOYMENT_SERVER "
      echo "$CI_REGISTRY_PASSWORD" | docker login $CI_REGISTRY -u "$CI_REGISTRY_USER" --password-stdin &&
      docker ps --filter name=palikkapalvelut* --filter status=running -aq | xargs docker rm --force; echo "Running containers stopped and removed" || true &&
      sleep 3 &&
      cd ~/code/microservices/palikkapalvelut &&
      docker compose -f docker-compose.prod.yml pull; echo "Pulled new image from registry" &&
      docker compose -f docker-compose.prod.yml up -d; echo "Started container" &&
      docker image prune -f; echo "Pruned dangling images"
      "
    - echo "Application successfully deployed."
  rules:
    - if: $CI_COMMIT_BRANCH == "main" # Rakennetaan vain main-branchista
```

## MkDocs-konfiguraatio

MkDocs luo staattisen sivuston sovelluksen dokumentaatiosta (`mkdocks.yml`)

