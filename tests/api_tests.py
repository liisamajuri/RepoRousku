"""
API-testit (PalikkaPalvelut)

Tämä moduuli sisältää API-testit GitLab-projektille. Näissä testeissä tarkastellaan erityisesti projektitietojen 
hakua eri token-tilanteissa: toimivalla, virheellisellä ja vanhentuneella tokenilla sekä jäsenyys- ja näkyvyystilanteita.

Huom: Tässä tiedostossa ei testata tapausta, jossa token puuttuu kokonaan. Tämä johtuu siitä, että sovelluksen 
käyttöliittymä (`start.py`) tarkistaa tokenin olemassaolon ennen API-kutsuja. Jos token puuttuu, sovellus 
näyttää virheilmoituksen käyttöliittymässä eikä aloita projektitietojen hakua. Tämän vuoksi puuttuvan tokenin 
tapaus testataan käyttöliittymän testauksen yhteydessä eikä osana API-testejä.
"""


import pytest
import os
from gitlab_api import ProjectData
from clockify_api import ClockifyData
import pandas as pd
from unittest.mock import patch


### MOCK-TOKENIT ###

MOCK_CLOCKIFY_TOKEN = "mock_clockify_token"
MOCK_GITLAB_TOKEN = "mock_gitlab_token"

@pytest.fixture(autouse=True)
def mock_env_tokens(monkeypatch):
    """
    Asettaa mock-tokenit ympäristömuuttujiin.
    """
    monkeypatch.setenv("CLOCKIFY_TOKEN", MOCK_CLOCKIFY_TOKEN)
    monkeypatch.setenv("GITLAB_TOKEN", MOCK_GITLAB_TOKEN)


### GITLAB-KOMPONENTTI ###

valid_token = os.getenv("GITLAB_TOKEN")
invalid_token = "12345-6789-012345678901234"
expired_token = "glpat-HUpy-42ye9m3oLFY5hPx"

own_project_url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
public_project_url = "https://gitlab.dclabra.fi/eerohu/tietokantojen-perusteet-ja-tietokantaohjelmointi"
private_project_url = "https://gitlab.dclabra.fi/kipe/devops-2024"

# Testataan eri tokeneja
@pytest.fixture
def valid_project():
    """Testiprojekti oikealla tokenilla."""
    return ProjectData(own_project_url, valid_token)

@pytest.fixture
def invalid_project():
    """Testiprojekti virheellisellä tokenilla."""
    return ProjectData(own_project_url, invalid_token)

@pytest.fixture
def expired_project():
    """Testiprojekti vanhentuneella tokenilla."""
    return ProjectData(own_project_url, expired_token)

def test_project_meta_data_with_valid_token(valid_project):
    """Testataan projektitietojen hakua oikealla tokenilla."""
    print("Testataan projektitietojen hakua oikealla tokenilla")
    meta_data = valid_project.get_project_meta_data()
    assert meta_data is not None
    assert isinstance(meta_data, dict)

def test_project_meta_data_with_invalid_token(invalid_project):
    """Testataan projektitietojen hakua virheellisellä tokenilla."""
    print("Testataan projektitietojen hakua virheellisellä tokenilla")
    meta_data = invalid_project.get_project_meta_data()
    assert meta_data is None

def test_project_meta_data_with_expired_token(expired_project):
    """Testataan projektitietojen hakua vanhentuneella tokenilla."""
    print("Testataan projektitietojen hakua vanhentuneella tokenilla")
    meta_data = expired_project.get_project_meta_data()
    assert meta_data is None
    
# Testataan eri näkyvyys- ja jäsenyystilanteita
@pytest.fixture
def public_project():
    """Testiprojekti julkisella URL:lla ilman jäsenyyttä."""
    return ProjectData(public_project_url, valid_token)

@pytest.fixture
def private_project_no_access():
    """Testiprojekti yksityisellä URL:lla ilman jäsenyyttä."""
    return ProjectData(private_project_url, valid_token)

def test_public_project_no_access(public_project):
    """Testataan julkisen projektin hakua ilman jäsenyyttä."""
    print("Testataan julkisen projektin hakua ilman jäsenyyttä")
    meta_data = public_project.get_project_meta_data()
    assert meta_data is not None, "Julkisen projektin tietojen haku pitäisi onnistua ilman jäsenyyttä"

def test_private_project_no_access(private_project_no_access):
    """Testataan yksityisen projektin hakua ilman jäsenyyttä."""
    print("Testataan yksityisen projektin hakua ilman jäsenyyttä")
    meta_data = private_project_no_access.get_project_meta_data()
    assert meta_data is None, "Yksityisen projektin tietojen haku pitäisi epäonnistua ilman jäsenyyttä"
    

    
    
### CLOCKIFY-KOMPONENTTI ###

# Mockataan ClockifyData käytettäväksi testeissä
valid_clockify_token = os.getenv("CLOCKIFY_TOKEN")
invalid_clockify_token = "12345-6789-012345678901234"
clockify_url = "https://api.clockify.me/api/v1"
valid_workspace_id = "671fabab605d557fc5342652"
valid_project_id = "671fac534ce4600d320d577d"


### Pytest-fixturet ###
@pytest.fixture
def valid_clockify():
    """Palauttaa ClockifyData-olion oikealla tokenilla."""
    return ClockifyData(clockify_url=clockify_url, api_key=valid_clockify_token)


@pytest.fixture
def invalid_clockify():
    """Palauttaa ClockifyData-olion väärällä tokenilla."""
    return ClockifyData(clockify_url=clockify_url, api_key=invalid_clockify_token)


### Testit ###
def test_valid_get_workspaces(valid_clockify):
    """Testaa työtilojen hakua oikealla tokenilla Clockifysta."""
    workspaces = valid_clockify.get_workspaces()
    assert isinstance(workspaces, list), "Palautuksen pitäisi olla lista"
    assert len(workspaces) > 0, "Työtiloja pitäisi olla saatavilla"


def test_valid_get_projects(valid_clockify):
    """Testaa projektien hakua oikealla tokenilla Clockifysta."""
    valid_clockify.workspace_id = valid_workspace_id
    projects = valid_clockify.get_projects()
    assert isinstance(projects, list), "Palautuksen pitäisi olla lista"
    assert len(projects) > 0, "Projektien pitäisi olla saatavilla valitusta työtilasta"


def test_invalid_token_get_workspaces(invalid_clockify):
    """Testaa työtilojen hakua virheellisellä tokenilla."""
    workspaces = invalid_clockify.get_workspaces()
    assert workspaces == [], "Virheellisen tokenin pitäisi palauttaa tyhjä lista"


def test_get_projects_with_invalid_token(invalid_clockify):
    """Testaa projektien hakua virheellisellä tokenilla."""
    invalid_clockify.workspace_id = valid_workspace_id
    projects = invalid_clockify.get_projects()
    assert projects == [], "Virheellisen tokenin pitäisi palauttaa tyhjä lista projekteille"
    
    

### TESTIRAPORTTI ### 

def test_report_exists():
    """
    Testaa, että testiraportti on luotu ja tulostaa linkin raportin avaamiseksi selaimessa.
    """
    report_path = "tests/reports/api_test_report.html"
    assert os.path.isfile(report_path), "Testiraporttia ei löytynyt!"
    print(f"Avaa testiraportti selaimessa osoitteessa: http://localhost:8010/api_test_report.html")