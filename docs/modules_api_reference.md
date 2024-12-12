# RepoRouskun Moduulit ja API-dokumentaatio


Tässä dokumentaatiossa kuvataan RepoRouskun Python-koodin eri moduulien toiminnot ja funktiot.

---


## OHJELMAN ALOITUSSIVU

Dokumentaatio `start.py` -moduulista, joka käsittelee projektin aloitussivun ja tokenien syötön.

::: src.app_pages.start

---

## MAIN

Dokumentaatio `app.py` -moduulista, joka sisältää sovelluksen päätoiminnot ja navigaation.

::: src.app

---

## PROJEKTIN TIEDOT

Dokumentaatio `project.py` -moduulista, joka näyttää projektin keskeiset tiedot ja visualisoi ne käyttäjälleen.

::: src.app_pages.project

---

## JÄSENET

Dokumentaatio `members.py` -moduulista, joka sisältää funktiot projektiryhmän jäsenten tietojen käsittelyyn.

::: src.app_pages.members

---

## GITLAB-INTEGRAATIO

Dokumentaatio `gitlab_api.py` -moduulista, joka sisältää luokan GitLabin tietojen hakuun ja käsittelyyn.

::: src.gitlab_api

---

## CLOCKIFY-INTEGRAATIO

Dokumentaatio `clockify_api.py` -moduulista, joka sisältää luokan Clockifyn tietojen hakuun ja käsittelyyn.

::: src.clockify_api

---

## KOMPONENTIT

Dokumentaatio `components.py` -moduulista, joka sisältää useita erilaisia komponentteja, kuten sivun otsikon ja graafisten esitysten luomisen, joita käytetään useissa eri näkymissä.

::: src.libraries.components

---

## TOKENIT

Dokumentaatio `env_tokens.py` -moduulista, joka sisältää tokenien käsittelyyn liittyvät funktiot.

::: src.libraries.env_tokens

---

## SALAUS

Dokumentaatio `encryption.py` -moduulista, joka sisältää tokenien salaukseen liittyvät funktiot. Tokenien salausta ei ole käytössä ohjelmistossa, mutta tässä oiva jatkokehityskohde. 

::: src.libraries.encryption

---

## INBOUND API

Dokumentaatio  `api/main.py` -moduulista, joka määrittelee RepoRouskun tarjoaman APIn.

::: api.main

---

## YKSIKKÖTESTAUS

Dokumentaatio `unit_tests.py` moduulista.

::: tests.unit_tests

---

## INTEGRAATIOTESTAUS

Dokumentaatio `integration_tests.py` moduulista.

::: tests.unit_tests

---

## OUTBOUND APIn TESTAUS

Dokumentaatio `api_tests.py` moduulista, joka testaa tietojen hakua GitLabista ja Clockifystä.

::: tests.api_tests

---

## INBOUND APIn TESTAUS

Yleiskuvaus .rest-testitiedostoista löytyy [täältä](rest_tests.md) ja yksityiskohtaisempi Swagger-dokumentaatio löytyy [täältä](http://localhost:8088/docs).