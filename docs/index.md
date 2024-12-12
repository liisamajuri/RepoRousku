![reporousku_logo1](images/logo_teksti_mkdocs.png)
# Tervetuloa RepoRouskuun!

RepoRousku on mikropalvelu, joka tarjoaa kattavan näkymän GitLab-repositorioprojektiin. Tämä ohjelma on rakennettu Streamlitillä, Pythonilla ja sillä noudetaan dataa GitLabista ja Clockifystä REST API -rajapintojen avulla. 


_Olitpa projektitiimin jäsen tai opettaja, RepoRousku antaa sinulle hyvän käsityksen projektin tilasta visualisoiden kaiken tarvittavan käyttäjäystävälliseen käyttöliittymään._

## Ominaisuudet

* **GitLab & Clockify integraatiot:** Yhdistä RepoRousku GitLabiin sekä Clockifyihin ja hae projektitietoja, kuten avoimien tai suljettujen issueiden lukumäärät, projektitiimin jäsenet ja heidän projektiin käyttämänsä aika. 

* **Tiimin jäsenien tilastot:** Näe ja analysoi tiimin jäseniin liittyviä tilastoja, kuten avoimia tehtäviä ja tuntikertymää.

* **Mukautettavat hallintapaneelit:** Luo visuaalisia esityksiä projektin mittareista, kuten palkkikaavioita ja donitsikaavioita, ja hahmota projektin eteneminen yhdellä silmäyksellä.

* **API-käyttö:** Käytä REST APIa hakeaksesi tarvittavia projekti- ja tuntitietoja RepoRouskun tarjoamasta API-rajapinnasta.

## Teknologiat 

* **Python & Streamlit:** RepoRouskun ydin on kehitetty Pythonilla ja Streamlitillä interaktiivisen ja selkeän verkkokäyttöliittymän luomiseksi.

* **Docker:** Mikropalvelu on kontitettu Dockerilla, mikä mahdollistaa helpon käyttöönoton ja skaalautuvuuden.

* **GitLab CI/CD:** Sovelluksen automatisoitu testaus tapahtuu GitLabin CI/CD-putkien avulla.



## Aloitus


_Yksityiskohtaisemmat käytön ohjeet löydät [täältä](http://localhost:8502/usage/)_ (eli _käyttöohjeet_ otsikon alta)


### Voit aloittaa RepoRouskun dev-käytön seuraavilla pikaohjeilla

**Kloonaa repositorio:** Kloonaa RepoRousku-repositorio paikalliseen ympäristöösi.
```python
git clone git@gitlab.dclabra.fi:projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut.git
```

**Käynnistä sovellus:** Käytä Dockeria RepoRousku-kontin rakentamiseen ja ajamiseen.
```python
docker compose -f docker-compose.dev.yml up --build
```

## Riippuvuudet

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.

## Dokumentaation yleiskatsaus

* **[Käyttöohje](http://localhost:8502/usage/):** Yksityiskohtaiset ohjeet RepoRouskun käyttämiseen, mukaan lukien ominaisuuksien kuvaukset ja käyttöliittymän toiminnot.
* **[Koodidokumentaatio](http://localhost:8502/modules_api_reference/):** Kattava sepostus RepoRouskussa käytetyistä ohjelmakokonaisuuksista, moduleista ja funktioista, sisältäen mkdocsilla automaattisesti generoitua koodidokumentaatiota.
* **[Konfiguraatio](http://localhost:8502/configuration/):** Ohjeet mikropalvelun konfigurointiin, mukaan lukien Dockerin ja CI/CD asetukset.

## Osallistuminen

Otamme mielellämme vastaan kontribuutioita! Jos haluat osallistua RepoRouskun kehittämiseen, voit lähettää pull requestin. Varmistathan että muutoksesi on hyvin dokumentoitu ja testattu ennen lähettämistä. 

### Kootut jatkokehitysideat
- **Clockify-tuntien täsmäytys:** Joku pirulainen aiheuttaa sen, että jossain tilanteessa tuntimäärät heittävät. Onko vika datassa vai datan käsittelyssä?
- **Työtunnit aikasarjana:** Olisi mahtavaa näyttää työtunnit aikasarjana pylväskaavioon projektin dashboardille.
- **Docker imagen laihis:** Docker imagea voitaisiin kuristaa pienemmäksi, jotta deployment olisi vieläkin tehokkaapaa.
- **Tokenien tallennusmahdollisuus myös koulun palvelimella:** Voisiko jatkokehityksen avulla saada Gitlab- ja Clockify-tokenit tallennetuksi esimerkiksi selaimen kekseihin / gitlab secretsiin. RepoRouskuun on kehitetty tokenien tallennus ympäristötiedostoon on soveltuva vain paikalliseen ajoon.
- **Tokenien salaus:** src/libraries/encryption.py:ssä on jo hyvää pohjaa tähän ideaan.
- **Jatkokehitys kurssien raportointi- ja arviointityökaluksi:**
    - Projektilaisen dashboardin voisi viimeistellä niin, että siitä olisi jopa projektikurssien raportointityökaluksi
    - Rouskuttimessa voisi olla mahdollisuus asettaa kriteeristö projektilaisen työmäärän arviointia varten (esim. tavoiteltavat tunti- ja issuemäärät)
- **Mahdollisuus tarkastella työtunteja myös Clockifyn taskien perusteella:** Nykyisessä RepoRouskun versiossa on tuettuna Clockifyn tagit.
- **Testikattavuuden nosto:** Jos mielesi tekee rakennella testejä, tästä löydät hyvän pohjan!
- **Alias-ongelma:** Jatkokehityskohteena olisi keksiä ratkaisu, kuinka yhdistetään yhden projektijäsenen tiedot, jos hänellä on Gitissä ja GitLabissa eri käyttäjänimet
- **Kieliversiot:** Jatkokehitysideana on toteuttaa RepoRousku muutamalla eri kielellä. Tämän hetkinen kieli on "finglish", mutta koodi on toteutettu niin, että kielivaihtoehtojen lisääminen onnistuu yksinkertaisesti. 


## Lisenssi

RepoRousku on julkaistu MIT-lisenssillä. Ohjelmalla ei ole mitään takuuta eikä PalikkaPalvelut vastaa ohjelman virheistä johtuneista seuraamuksista.
