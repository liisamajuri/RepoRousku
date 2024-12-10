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

**Kloonaa repo komennolla:** 
```bash
git clone git@gitlab.dclabra.fi:projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut.git
```
**Jos haluat ensin tarkastella tarkempaa käyttöliittymäohjetta tai tarkempaa koodidokumentaatiota, aja projektin juurikansiossa komennot:**

```bash
chmod +x docs/serve_docs.sh
./docs/serve_docs.sh
```

***

<!-- KÄYTTÖYMPÄRISTÖ -->
### KÄYTTÖYMPÄRISTÖ (DEV)

**Docker imagen buildaus ja konttien käynnistys projektin juurikansiossa:**

```bash
docker compose -f docker-compose.dev.yml up --build
```

**Kontit alas:**
```bash
docker compose -f docker-compose.dev.yml down
```

***

<!-- RIIPPUVUUDET -->
### RIIPPUVUUDET

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.


***

<!-- MODUULIT JA OHJELMAKOKONAISUUDET-->
**API**

**DOCS**

**SRC**

**TESTS**



***

<!-- DOKUMENTAATIO -->
## DOKUMENTAATIO


* Käyttöliittymä tarkasteltavissa sivulla: http://localhost:8501
* Testiraportti tarkasteltavissa sivulla: http://localhost:8010
* Koodidokumentaatio tarkasteltavissa sivulla: http://localhost:8502/
* api-dokumentaatio tarkasteltavissa sivulla: http://localhost:8088/docs

<br>


- Projektikurssin Reppu-ympäristö: [_Projektiopinnot 4 - Digitaaliset palvelut_](https://reppu.kamk.fi/course/view.php?id=1451)
- Ohjelman vaatimukset: [_Vaatimusmäärittely_](https://gitlab.dclabra.fi/wiki/v8kBWGJpSLGDysLJMLUIsw)
- Tiimin Scrum-palaveridokumentaatio [_Projektiblogi_](https://gitlab.dclabra.fi/wiki/WlaG1MzxSmCmUx31mzz4Aw)
- Ohjelman testaus: [_Testaussuunnitelma_](https://gitlab.dclabra.fi/wiki/g2UW2QM6TzG6xkVaMlMeZg)
- Ohjelman käyttöliittymäsuunnitelma: [_Käyttöliittymäsuunnitelma_](https://gitlab.dclabra.fi/wiki/EKt-cLrXTvOSyllLJq12Tg)

***

