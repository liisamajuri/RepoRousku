# Projekti 4 - PalikkaPalvelut


***

## Sisällysluettelo

- [YLEISET TIEDOT](#yleiset-tiedot)
- [PROJEKTIN KUVAUS](#projektin-kuvaus)
- [REPOSITORION SISÄLTÖ](#repositorion-sisältö)
- [ALOITTAMINEN](#aloittaminen)
  - [KÄYTTÖYMPÄRISTÖ](#käyttöympäristö)
  - [RIIPPUVUUDET](#riippuvuudet)
- [KÄYTTÖ](#käyttöohjeita)
  - [MODUULIT](#moduulit)
  - [OHJELMAKOKONAISUUDET](#ohjelmakokonaisuudet)
  - [MODUULIEN KUVAUKSET](#moduulien-kuvaukset)
  - [OHJELMIEN KUVAUKSET](#ohjelmien-kuvaukset)
- [DOKUMENTAATIO](#dokumentaatio)

***
<!-- YLEISET TIEDOT -->
## YLEISET TIEDOT
- **Nimi:** [Palikkapalvelut](https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut)
- **Tekijät:** Hakkarainen, Nadina; Majuri, Liisa; Mikkola, Henna; Tishchenko, Vladimir
- **Ryhmätunnus:** TTM22SAI
- **Organisaatio:** Kajaanin ammattikorkeakoulu (KAMK)
- **Projektiin käytetyt tunnit:** XXX

***

<!-- PROJEKTIN KUVAUS -->
## PROJEKTIN KUVAUS

RepoRousku on mikropalvelupohjainen sovellus, joka tarjoaa yhdellä silmäyksellä GitLab-repositorioprojektin tilan, koostaen projektihallinnan näkökulmasta projektin keskeisimmät tunnusluvut sekä projektitiimiläisten tuntitiedot yhteen näkymään. 

Tämä ohjelma on rakennettu Streamlitillä, Pythonilla ja sillä noudetaan dataa GitLabista ja Clockifystä REST API -rajapintojen avulla. Dockerilla kontitettu ympäristö mahdollistaa sovelluksen helpon käyttöönoton.

***

<!-- REPOSITORION SISÄLTÖ -->
## REPOSITORION SISÄLTÖ

#### Repositorion hakemistorakenne:
```
Palikkapalvelut/
|-- docs/
|   |-- images/
|   |-- configuration.md
|   |-- index.md
|   |-- modules_api_reference.md
|   |-- usage.md
|-- site/
|-- src/
|   |-- .streamlit/
|   |   |-- config.toml
|   |-- app_pages/
|   |   |-- gitlab_link.py
|   |   |-- members.py
|   |   |-- project.py
|   |   |-- start.py
|   |-- libraries/
|   |   |-- components.py
|   |-- images/
|   |-- app.py
|   |-- gitlab_api.py
|-- tests/
|   |-- reports/
|   |-- api_tests.py
|   |-- unit_tests.py
|-- Dockerfile
|-- docker-compose.yml
|-- mkdocs.yml
|-- README.md
|-- requirements.txt
```

Hakemistorakenne sisältää kaikki tarvittavat komponentit, kuten dokumentaation, sovelluksen lähdekoodin, testit ja Docker-konfiguraatiotiedostot.

***

<!-- ALOITTAMINEN -->
## ALOITTAMINEN

1. **Kloonaa repo komennolla:** 
```bash
git clone git@gitlab.dclabra.fi:projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut.git
```
2. **Jos haluat ensin tarkastella tarkempaa käyttöliittymäohjetta tai koodidokumentaatiota, aja projektin juurikansiossa komennot:**

```bash
chmod +x docs/serve_docs.sh
./docs/serve_docs.sh
```

***

<!-- KÄYTTÖYMPÄRISTÖ -->
### KÄYTTÖYMPÄRISTÖ

**YMPÄRISTÖN PYSTYTTÄMINEN:**

- **Aja projektin juurikansiossa komento:**

```shell=
docker-compose up
```

**YMPÄRISTÖN ALASAJO:**

* **Aja projektin juurikansiossa komento:**

```shell=
docker-compose down
```


***

<!-- RIIPPUVUUDET -->
### RIIPPUVUUDET

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.


***

<!-- KÄYTTÖ -->
## KÄYTTÖOHJEITA

### Personal Access Tokenin lisääminen ympäristömuuttujaan
- Bash-terminaali:
  ```
  # Varmista, että olet kotihakemistossa:
  cd ~
  
  # Avaa .bashrc-tiedosto muokattavaksi:
  nano .bashrc
  
  # Lisää tiedoston loppuun seuraava rivi (vaihda "YOUR_GITLAB_TOKEN" token-arvoon):
  export GITLAB_TOKEN="YOUR_GITLAB_TOKEN"
  
  # Tallenna ja sulje tiedosto:
  Paina Ctrl + O
  Paina Enter
  Paina Ctrl + X
  
  # Lataa päivitetty .bashrc-tiedosto: 
  source ~/.bashrc
  
  # Varmista ympäristömuuttujan tallentuminen:
  echo $GITLAB_TOKEN
  ```
  - Ympäristömuuttujaan tallennetun tokenin käyttö:
      - *docker-compose.yml*:
      ```
      ...
        ...
          environment:
            GITLAB_TOKEN: "${GITLAB_TOKEN}"

      ```
      - *app\.py* tms. kooditiedosto:
      ```
      gitlab_token = os.getenv("GITLAB_TOKEN")
      ```



### TESTAUS

==HUOM!== 

Etsitään tälle järkevämpi paikka README:ssä, nyt vain kirjattu komennot talteen.

**Ruff**-linterin käyttö koodin tyyli- ja syntaksivirheiden tunnistamiseen ja korjaamiseen:
- Asennetaan  ja suoritetaan automaattisesti kontin käynnistyksen yhteydessä (`docker compose up`)
- Ruff-testin suorittaminen kontin pystytyksen jälkeen *src*-kansion koodien tarkistukseen (`docker-compose run --rm palikka ruff check src -v`)

**Yksikkötestit** funktioiden ja luokkien yms. testaukseen:
- Asennetaan  ja suoritetaan automaattisesti kontin pystytyksessä (`docker compose up`)
- Yksikkötestien suorittaminen kontin käynnistyksen jälkeen (`docker-compose run --rm palikka pytest -v -s --tb=short --html=tests/reports/unit_test_report.html --self-contained-html tests/unit_tests.py`)


***

<!-- MODUULIT JA OHJELMAKOKONAISUUDET-->
### MODUULIT



### OHJELMAKOKONAISUUDET

* **gitlab_link.py:** Vastaa GitLab-linkkien avaamisesta ja navigoinnista.
* **members.py:** Näyttää projektiryhmän jäsenten tiedot ja tilastot.
* **project.py:** Esittää projektin keskeiset tiedot ja metriikat visuaalisesti.
* **start.py:** Projektin aloitussivu, joka sisältää pääsytietojen syötön.
* **components.py:** Erilaisia visuaalisia komponentteja, kuten donitsikaavioita ja otsikoita, jotka käytetään eri näkymissä.
* **app.py:** Sovelluksen pääohjelma, joka yhdistää eri ohjelmakokonaisuudet ja mahdollistaa käyttöliittymän toiminnan Streamlitissä.



***

<!-- MODUULIEN JA OHJELMIEN KUVAUKSET -->
### MODUULIEN KUVAUKSET


### OHJELMIEN KUVAUKSET


***

<!-- DOKUMENTAATIO -->
## DOKUMENTAATIO

- Projektikurssin Reppu-ympäristö: [_Projektiopinnot 4 - Digitaaliset palvelut_](https://reppu.kamk.fi/course/view.php?id=1451)
- Ohjelman vaatimukset: [_Vaatimukset-dokumentaatio_](Tähän linkki)
- Ohjelman testaus: [_Testausdokumentaatio_](Tähän linkki)
- 

***

