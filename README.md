# Projekti 4 - PalikkaPalvelut


***

## Sisällysluettelo

- [YLEISET TIEDOT](#yleiset-tiedot)
- [PROJEKTIN KUVAUS](#projektin-kuvaus)
- [REPOSITORION SISÄLTÖ](#repositorion-sisältö)
- [ALOITTAMINEN](#aloittaminen)
  - [KÄYTTÖYMPÄRISTÖ](#käyttöympäristö)
  - [RIIPPUVUUDET](#riippuvuudet)
- [KÄYTTÖ](#käyttö)
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

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

***

<!-- REPOSITORION SISÄLTÖ -->
## REPOSITORION SISÄLTÖ

#### Repositorion hakemistorakenne:

***

<!-- ALOITTAMINEN -->
## ALOITTAMINEN

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


***

<!-- KÄYTTÖYMPÄRISTÖ -->
### KÄYTTÖYMPÄRISTÖ



##### **YMPÄRISTÖN PYSTYTTÄMINEN:**

- Aja projektin juurikansiossa komento

```shell=
docker-compose up
```


##### **YMPÄRISTÖN ALASAJO _(tarvittaessa)_ :**

- Aja projektin juurikansiossa komento

```shell=
docker-compose down
```


***

<!-- RIIPPUVUUDET -->
### RIIPPUVUUDET

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.

***

<!-- ETL -->
### ETL


***

<!-- KÄYTTÖ -->
## KÄYTTÖ

**TESTAUS**

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

***

