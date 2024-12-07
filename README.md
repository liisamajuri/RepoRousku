# Projekti 4 - PalikkaPalvelut


***

## Sisällysluettelo

- [YLEISET TIEDOT](#yleiset-tiedot)
- [PROJEKTIN KUVAUS](#projektin-kuvaus)
- [REPOSITORION SISÄLTÖ](#repositorion-sisältö)
- [ALOITTAMINEN](#aloittaminen)
  - [KÄYTTÖYMPÄRISTÖ](#käyttöympäristö)
  - [RIIPPUVUUDET](#riippuvuudet)
- [TESTAUS](#testaus)
- [MODUULIT](#moduulit)
- [DOKUMENTAATIO](#dokumentaatio)

***
<!-- YLEISET TIEDOT -->
## YLEISET TIEDOT
- **Nimi:** [Palikkapalvelut](https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut)
- **Tekijät:** Hakkarainen, Nadina; Majuri, Liisa; Mikkonen, Henna; Tishchenko, Vladimir
- **Ryhmätunnus:** TTM22SAI
- **Organisaatio:** Kajaanin ammattikorkeakoulu (KAMK)
- **Projektiin käytetyt tunnit:** XXX

***

<!-- PROJEKTIN KUVAUS -->
## PROJEKTIN KUVAUS

RepoRousku on mikropalvelupohjainen sovellus, joka tarjoaa yhdellä silmäyksellä GitLab-repositorioprojektin tilan, koostaen projektihallinnan näkökulmasta projektin keskeisimmät tunnusluvut sekä projektitiimiläisten tuntitiedot yhteen näkymään. 

Tämä ohjelma on rakennettu mm. seuraavilla teknologioilla:

*  **Streamlit**: Frontend- ja käyttöliittymä
* **Python**: Backend- ja logiikkatoiminnot
* **REST API**: Datan haku GitLabista ja Clockifystä
* **Docker**: Kontitetut ympäristöt 
* **CI/CD**: Ohjelman testit, dokumentaatio sekä deployaus tapahtuvat automaattisesti. 

***

<!-- REPOSITORION SISÄLTÖ -->
## ==REPOSITORION SISÄLTÖ==

#### Repositorion hakemistorakenne:
```
Palikkapalvelut/
|-- api/
    |-- main.py
|-- docs/
|   |-- images/
|   |-- configuration.md
|   |-- index.md
|   |-- modules_api_reference.md
|   |-- serve_docs.sh
|   |-- usage.md
|-- requests/
|   |-- clockify_requests.rest
|   |-- functionality_check.rest
|   |-- gitlab_requests.rest
|-- site/
|-- src/
|   |-- .streamlit/
|   |   |-- config.toml
|   |-- app_pages/
|   |   |-- members.py
|   |   |-- project.py
|   |   |-- start.py
|   |-- libraries/
|   |   |-- components.py
|   |   |-- encryption.py
|   |   |-- env_tokens.py
|   |-- images/
|   |-- app.py
|   |-- clockify_api.py
|   |-- gitlab_api.py
|-- tests/
|   |-- reports/
|   |-- api_tests.py
|   |-- unit_tests.py 
|   |-- unit_tests.py
|-- .env
|-- .gitignore
|-- .gitlab-ci.yml
|-- Dockerfile
|-- docker-compose.yml
|-- mkdocs.yml
|-- pytest.ini
|-- README.md
|-- requirements.txt
```

Hakemistorakenne sisältää kaikki tarvittavat komponentit, kuten dokumentaation, sovelluksen lähdekoodin, testit, deploymentin sekä Docker-konfiguraatiotiedostot.

***

<!-- ALOITTAMINEN -->
## ALOITTAMINEN

### REPOSITORION KLOONAUS

**Kloonaa repo komennolla:**

```bash
git clone git@gitlab.dclabra.fi:projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut.git
```

Repositorion kloonaamisen jälkeen koodidokumentaatiota on mahdollista tarkastella paikallisesti ilman docker-konttien käynnistämistä:

```bash
chmod +x docs/serve_docs.sh
./docs/serve_docs.sh
```

***

<!-- KÄYTTÖYMPÄRISTÖ -->
### KÄYTTÖYMPÄRISTÖ

**YMPÄRISTÖN PYSTYTTÄMINEN:**

Aja projektin juurikansiossa: 

**Docker imagen buildaus:**

```shell=
docker compose build
```

**Kaikkien konttien käynnistys:**

```shell=
docker compose up
```

**Pelkän Streamlit-sovellus -kontin käynnistys:**

```shell=
docker compose up streamlit
```

**Pelkän testikontin käynnistys:**

```shell=
docker compose up tests
```

**Pelkän testiraporttikontin käynnistys:**

```shell=
docker compose up reports
```

**Pelkän dokumentaatiokontin käynnistys:**

```shell=
docker compose up docs
```

**Pelkän apikontin käynnistys:**
```shell=
docker compose up api
```

**Konttien käynnistämisen jälkeen:**

- Käyttöliittymä tarkasteltavissa sivulla: http://localhost:8501
- Testiraportti tarkasteltavissa sivulla: http://localhost:8010
- Koodidokumentaatio tarkasteltavissa sivulla: http://localhost:8502/
- api-rajapinta sivulla: http://localhost:8088
- api-dokumentaatio tarkasteltavissa sivulla: http://localhost:8088/docs



**YMPÄRISTÖN ALASAJO:**

Aja projektin juurikansiossa komento:

```shell=
docker compose down
```


***

<!-- RIIPPUVUUDET -->
### RIIPPUVUUDET

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.

***

## TESTAUS

**Ruff**-linterin käyttö koodin tyyli- ja syntaksivirheiden tunnistamiseen ja korjaamiseen:
- Asennetaan  ja suoritetaan automaattisesti kontin käynnistyksen yhteydessä (`docker compose up`)
- Ruff-testin suorittaminen kontin pystytyksen jälkeen *src*-kansion koodien tarkistukseen (`docker-compose run --rm palikka ruff check src -v`)

**Yksikkötestit** funktioiden ja luokkien yms. testaukseen:
- Asennetaan  ja suoritetaan automaattisesti kontin pystytyksessä (`docker compose up`)
- Yksikkötestien suorittaminen kontin käynnistyksen jälkeen (`docker-compose run --rm palikka pytest -v -s --tb=short --html=tests/reports/unit_test_report.html --self-contained-html tests/unit_tests.py`)

### API-rajapinnan testaamiseen käytettävä REST Client

Tässä projektissa käytetään **REST Client** -laajennusta API-pyyntöjen testaamiseen. Seuraavilla ohjeilla voit asentaa REST Clientin ja käyttää sitä helposti.
#### Asennusohjeet

1. Avaa **Visual Studio Code**.
2. Siirry **Extensions**-näkymään:
   - Klikkaa vasemmassa reunassa olevaa **laajennusten kuvaketta** (ikonissa on neliö, jossa on pieni neliö sisällä).
   - Vaihtoehtoisesti voit painaa näppäinyhdistelmää `Ctrl+Shift+X`.
3. Kirjoita hakukenttään **"REST Client"** ja paina `Enter`.
4. Valitse **REST Client** ja klikkaa **Install**-painiketta.

#### Käyttöohjeet

1. Varmista, että olet asettanut ympäristömuuttujat, kuten `GITLAB_TOKEN`, `.env`-tiedostoon tai VS Code -asetuksiin. 
   - Katso lisätietoa ympäristömuuttujien asettamisesta projektin dokumentaatiosta.
2. Avaa projektin juurihakemistosta **`gitlab_requests.rest`**-tiedosto.
3. Klikkaa haluamasi HTTP-pyynnön vieressä näkyvää **Send Request** -painiketta.
4. REST Client suorittaa pyynnön ja näyttää vastauksen erillisessä paneelissa.

***

<!-- MODUULIT JA OHJELMAKOKONAISUUDET-->
## MODUULIT

Tarkemmat ohjelmakuvaukset löytyvät mkdocs-koodidokumentaatiosta `docs/`. 

### 1. **Käyttöliittymä ja pääohjelma**

Hakemisto: `src/`

**`app.py`**

RepoRouskun pääohjelma, joka vastaa sovelluksen navigoinnista ja ulkoasusta. Toteuttaa Streamlit-pohjaisen käyttöliittymän.

  **Tärkeimmät funktiot:**
  * `main()`: Sovelluksen pääkoodi, joka luo navigointivalikon ja aloittaa sovelluksen.
  * `create_navigation_panel()`: Navigointipaneelin luominen sovelluksen sivuille.
  * `set_appearance()`: Ulkoasun hallinta.


### 2. **Sovelluksen sivut**

Hakemisto: `src/app_pages/`

**`start.py`**

Aloitussivu, joka sisältää käyttöoikeustietojen (Access Token) syötön ja projektin asetukset.

  **Tärkeimmät funktiot:**
  * `start_page()`: Luo käyttöliittymän aloitussivun.
  * `get_project_data()`: Hakee projektin tiedot GitLabista.
  * `setup_clockify()`: Asettaa Clockify-integraation muuttujat.

<br>

**`project.py`**

 Esittää projektin keskeiset tiedot, kuten valmiusaste, jäsenet ja suljetut issuet.

  **Tärkeimmät funktiot:**
  * `project_page()`: Projektitietojen dashboardin luominen.
  * `milestone_donut()`: Milestonien visualisointi donitsikaaviona.
  * `closed_issues_by_milestone()`: Suljettujen issueiden analyysi milestoneittain.

 <br>
 
**`members.py`**

Näyttää projektiryhmän jäsenten statistiikat ja tiedot.

  **Tärkeimmät funktiot:**
  * `member_page()`: Dashboard jäsenten datan tarkasteluun.
  * `fetch_sprint_hours()`: Työtuntien haku ja tallennus.


### 3. **Komponentit**
Hakemisto: `src/libraries/`

**`components.py`**

Kokoelma visuaalisia elementtejä, kuten graafit ja otsikot.

  **Tärkeimmät funktiot:**
  * `make_donut()`: Luo donitsikaavion.
  * `make_page_title()`: Luo otsikkokomponentin.


### 4. **API-integraatiot**

**`gitlab_api.py`**

Vastaa GitLab-projektien tietojen hakemisesta.

  **Tärkeimmät funktiot:**
  * `get_commits()`: Palauttaa commitit.
  * `get_closed_issues()`: Palauttaa suljetut issuet.
  * `get_milestones()`: Palauttaa milestonejen tiedot.

<br>


**`clockify_api.py`**

Käsittelee Clockify-projektien tiedot, kuten työtunnit ja sprinttijärjestykset.

  **Tärkeimmät funktiot:**
  * `get_project_task_hours()`: Hakee tehtävät ja niiden tunnit.


### 5. **Tokenit ja salaus**
**`env_tokens.py`**

Ympäristömuuttujien käsittely, kuten tokenien tallennus ja poisto.

  **Tärkeimmät funktiot:**
  * `save_tokens_to_env()`: Tallentaa tokenit ympäristömuuttujiin.

<br>

**`encryption.py`**

Suunniteltu tokenien salausta varten.

  **Tärkeimmät funktiot:**
  * `encrypt_message()`: Salauksen toteutus.
  * `decrypt_message()`: Purkaa salatun viestin.


### 6. **Testit**

Hakemisto: `tests/`

**`unit_tests.py`**

Yksikkötestit ProjectData- ja ClockifyData-luokille.

  **Tärkeimmät funktiot:**
  * `test_get_milestones()`: Testaa milestone-tietojen haku.
  * `test_get_commits()`: Testaa commit-tietojen oikeellisuuden.

<br>

**`api_tests.py`**

Testaa API-rajapintojen toimivuutta.

  **Tärkeimmät funktiot:**
  * `test_valid_get_projects():` Testaa projektien haku oikealla tokenilla.

<br>

**`integration_tests.py`**

Integraatiotestit eri moduulien yhteistoiminnalle.


***

<!-- DOKUMENTAATIO -->
## DOKUMENTAATIO

- Projektikurssin Reppu-ympäristö: [_Projektiopinnot 4 - Digitaaliset palvelut_](https://reppu.kamk.fi/course/view.php?id=1451)
- Ohjelman vaatimukset: [_Vaatimukset-dokumentaatio_](Tähän linkki)
- Ohjelman testaus: [_Testausdokumentaatio_](Tähän linkki)
 

***

