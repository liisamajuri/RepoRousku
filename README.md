# Projekti 4 - PalikkaPalvelut


***

## Sisällysluettelo

- [YLEISET TIEDOT](#yleiset-tiedot)
- [PROJEKTIN KUVAUS](#projektin-kuvaus)
- [REPOSITORION SISÄLTÖ](#repositorion-sisältö)
- [OHJELMAKOKONAISUUDET](#ohjelmakokonaisuudet)
- [ALOITTAMINEN](#aloittaminen)
  - [KÄYTTÖYMPÄRISTÖ](#käyttöympäristö)
  - [RIIPPUVUUDET](#riippuvuudet)
- [KÄYTTÖ](#käyttöohjeita)
- [MODUULIT](#moduulit)
- [VAATIMUKSET](#vaatimukset)
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

### Repositorion hakemistorakenne:
```
Palikkapalvelut/
|-- .streamlit/
|   |--config.toml
|-- api/
|   |-- main.py
|-- docs/
|   |-- images/
|   |-- configuration.md
|   |-- index.md
|   |-- modules_api_reference.md
|   |-- serve_docs.sh
|   |-- usage.md
|-- requests/
|-- |-- clockify_requests.rest
|-- |-- functionality_check.rest
|-- |-- gitlab_requests.rest
|-- site/
|-- src/
|   |-- app_pages/
|   |   |-- members.py
|   |   |-- project.py
|   |   |-- start.py
|   |-- images/
|   |-- libraries/
|   |   |-- components.py
|   |   |-- encryption.py
|   |   |-- env_tokens.py
|   |-- app.py
|   |-- clockify_api.py
|   |-- gitlab_api.py
|-- tests/
|   |-- reports/
|   |-- api_tests.py
|   |-- integration_tests.py
|   |-- unit_tests.py
|-- .gitlab-ci.yml
|-- docker-compose.dev.yml
|-- docker-compose.prod.yml
|-- docker-compose.yml
|-- Dockerfile
|-- generate_rest_docs.py
|-- mkdocs.yml
|-- README.md
|-- requirements.txt
```

Hakemistorakenne sisältää kaikki tarvittavat komponentit, kuten dokumentaation, sovelluksen lähdekoodin, testit, API-rajapinnat, CI/CD-pipelinen sekä Docker-konfiguraatiotiedostot.

<!-- MODUULIT JA OHJELMAKOKONAISUUDET-->
### OHJELMAKOKONAISUUDET

#### Ohjelman aloitussivu

`start.py`

**Kuvaus:**

Tämä ohjelma muodostaa RepoRouskun aloitussivun, jossa käyttäjä syöttää projektin GitLab-URL:n ja tarvittavat Access Tokenit. Clockify-integraation avulla käyttäjä voi tarkistastella myös projektin ajankäyttöä. 


#### Pääohjelma

`app.py`

**Kuvaus:**

Sovelluksen pääohjelma, joka yhdistää kaikki toiminnallisuudet ja luo navigointivalikon eri näkymien välillä. 

**Keskeiset funktiot:**

* `create_navigation_panel()`: Luo navigointivalikon.
* `main()`: Käynnistää sovelluksen ja määrittää aloitussivun.
* `set_appearance()`: Hallitsee sovelluksen visuaalista ulkoasua.

#### Projekti tiedot

`project.py`

**Kuvaus:**

Tämä moduuli tarjoaa projektitietojen dashboardin, jossa käyttäjä voi tarkastella projektin valmiusastetta, suljettuja issueita, committeja ja milestoneja.

#### Käyttäjien tiedot

`members.py`

**Kuvaus:**

Dashboard, jossa käyttäjä voi tarkastella projektiryhmän jäsenten työtunteja ja kontribuutioita. Soveltuu erityisesti yksittäisen jäsenen suoritusten tarkasteluun.

#### Gitlab-integraation

`gitlab_api.py`

**Kuvaus:**

Vastaa GitLabin API-rajapinnan hyödyntämisestä projektidatan hakemiseen. Tämä moduuli sisältää ProjectData-luokan, joka tarjoaa jäsenneltyä dataa käyttöliittymälle.

**Keskeiset funktiot:**

* `count_open_issues()`: Palauttaa avoimien issueiden määrän.
* `get_commits_by_date(members, min_date, max_date)`: Hakee commitit aikajakson perusteella.
* `get_milestones()`: Palauttaa projektin milestone-tiedot.
* `get_readiness_issues()`: Laskee projektin valmiusasteen issueiden perusteella.

#### Clockify-integraatio

`clockify_api.py`

**Kuvaus:**

Hoitaa Clockify-rajapinnan kautta projektin työaikatietojen noutamisen ja analysoinnin.

**Keskeiset funktiot:**
* `get_all_user_hours_df()`: Palauttaa kaikkien käyttäjien työtunnit DataFrame-muodossa.
* `get_tag_hours()`: Laskee tunnit kullekin tagille.
* `get_sprint_hours()`: Yhdistää sprinttikohtaiset työtunnit milestoneihin.

#### Inbound API

`api/main.py`

**Kuvaus:**

Määrittelee RepoRouskun tarjoaman FastAPI-rajapinnan. Tämä API mahdollistaa projektin tietojen haun suoraan RepoRouskun kautta.

#### Testaus

`unit_tests.py`, `integration_tests.py`, `api_tests.py`

**Kuvaus:**

Testimoduulit kattavat RepoRouskun eri toiminnallisuudet, kuten yksikkötestit (luokat ja funktiot), integraatiotestit (API-rajapinnat) ja ulkoiset API-kutsut (GitLab ja Clockify).



Tämä dokumentaatio tarjoaa yleiskatsauksen moduuleista. Yksityiskohtainen tekninen kuvaus on saatavilla projektin mkdocs-dokumentaatiossa.



***

<!-- ALOITTAMINEN -->
## ALOITTAMINEN

**Kloonaa repo komennolla:** 
```bash
git clone git@gitlab.dclabra.fi:projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut.git
```
**Jos haluat ensin tarkastella tarkempaa käyttöliittymäohjetta tai koodidokumentaatiota, aja projektin juurikansiossa komennot:**

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
<!-- VAATIMUKSET -->
## VAATIMUKSET

Projektin tarkoituksena on toteuttaa Streamlitillä interaktiivinen käyttöliittymä, joka tarjoaa visuaalisen esityksen projektin keskeisistä tiedoista, kuten milestonejen edistymisestä, tiimin suorituskyvystä, tiimin projektiin käyttämistä tunneista ja muista projektin metriikoista. Käyttäjä voi valita tarkasteltavaa dataa ajan tai käyttäjän perusteella ja tutkia tietoa dynaamisesti erilaisten kaavioiden avulla. 

Ohjelmakoodi on toteutettu ja dokumentoitu kauttaaltaan niin, että se mahdollistaa API-rajapintojen laajentamisen sekä ohjelman jatkokehittämisen.  

**Toiminnallisista** ja **ei toiminnallisista vaatimuksista** sekä niiden täyttymisestä voit lukea lisää vaatimusmäärittely-[dokumentista](https://gitlab.dclabra.fi/wiki/v8kBWGJpSLGDysLJMLUIsw?both#Toiminnalliset-vaatimukset).


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

