![reporousku_logo1](images/logotext.png)
# Tervetuloa RepoRouskuun!

RepoRousku on mikropalvelu, joka tarjoaa kattavan näkymän GitLab-repositorioprojektiin. Tämä ohjelma on rakennettu Streamlitillä, Pythonilla ja sillä noudetaan dataa GitLabista ja Clockifystä REST API -rajapintojen avulla. 

!!!tip testitekstiä

_Olitpa projektitiimin jäsen tai opettaja, RepoRousku antaa sinulle hyvän käsityksen projektin tilasta visualisoiden kaiken tarvittavan käyttäjäystävälliseen käyttöliittymään._

## Ominaisuudet

* **GitLab-integraatio:** Yhdistä GitLabiin sekä Clockifyihin ja hae projektitietoja, kuten issueiden lukumäärä, projektitiimin jäsenet ja heidän projektiin käyttämänsä aika. 

* **Tiimin jäsenien tilastot:** Näe ja analysoi tiimin jäseniin liittyviä tilastoja, kuten avoimia tehtäviä ja kontribuutioita.

* **Mukautettavat hallintapaneelit:** Luo visuaalisia esityksiä projektin mittareista, kuten palkkikaavioita ja donitsikaavioita, ja hahmota projektin eteneminen yhdellä silmäyksellä.

* **API-käyttö:** Käytä REST APIa hakeaksesi tarvittavia projekti- ja tuntitietoja.

## Teknologiat 

* **Python & Streamlit:** RepoRouskun ydin on kehitetty Pythonilla ja Streamlitillä interaktiivisen ja selkeän verkkokäyttöliittymän luomiseksi.

* **Docker:** Mikropalvelu on kontitettu Dockerilla, mikä mahdollistaa helpon käyttöönoton ja skaalautuvuuden.

* **GitLab CI/CD:** Sovelluksen automatisoitu testaus tapahtuu GitLabin CI/CD-putkien avulla.

## Aloitus

Voit aloittaa RepoRouskun käytön seuraavilla ohjeilla:

**Kloonaa repositorio:** Kloonaa RepoRousku-repositorio paikalliseen ympäristöösi.
```python
git clone https://gitlab.com/your-repo/repo-rouska.git
```

**Käynnistä sovellus:** Käytä Dockeria RepoRousku-kontin rakentamiseen ja ajamiseen.
```python
docker-compose up --build
```

## Riippuvuudet

Erikseen asennettavat kirjastot on koottu erilliseen **_requirements.txt_**-tiedostoon. Kirjastot asennetaan Docker-kontin pystytyksen yhteydessä automaattisesti.

## Dokumentaation yleiskatsaus

* **[Käyttöohje](http://127.0.0.1:8000/usage/):** Yksityiskohtaiset ohjeet RepoRouskun käyttämiseen, mukaan lukien ominaisuuksien kuvaukset ja käyttöliittymän toiminnot.
* **[Moduulit ja API-dokumentaatio](http://127.0.0.1:8000/modules_api_reference/):** Kattava sepostus RepoRouskussa käytetyistä funktioista ja moduuleista, sisältäen automaattisesti generoituja dokumentaatioita.

* **[Konfiguraatio](http://127.0.0.1:8000/configuration/):** Ohjeet mikropalvelun konfigurointiin, mukaan lukien Dockerin ja CI/CD asetukset.

## Osallistuminen

Otamme mielellämme vastaan kontribuutioita! Jos haluat osallistua RepoRouskun kehittämiseen, voit lähettää pull requestin. Varmistathan että muutoksesi on hyvin dokumentoitu ja testattu ennen lähettämistä. 

## Lisenssi

RepoRousku on julkaistu MIT-lisenssillä. Ohjelmalla ei ole mitään takuuta eikä PalikkaPalvelut vastaa ohjelman virheistä johtuneista seurauksista.
