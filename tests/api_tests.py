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

valid_token = os.getenv("GITLAB_TOKEN")
invalid_token = "12345-6789-012345678901234"
expired_token = "glpat-HUpy-42ye9m3oLFY5hPx"

own_project_url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
internal_project_url = "https://gitlab.dclabra.fi/mikaker/mobiili-ohjelmointi"
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
def internal_project():
    """Testiprojekti sisäisellä URL:lla ilman jäsenyyttä."""
    return ProjectData(internal_project_url, valid_token)

@pytest.fixture
def private_project_no_access():
    """Testiprojekti yksityisellä URL:lla ilman jäsenyyttä."""
    return ProjectData(private_project_url, valid_token)

def test_public_project_no_access(public_project):
    """Testataan julkisen projektin hakua ilman jäsenyyttä."""
    print("Testataan julkisen projektin hakua ilman jäsenyyttä")
    meta_data = public_project.get_project_meta_data()
    assert meta_data is not None, "Julkisen projektin tietojen haku pitäisi onnistua ilman jäsenyyttä"

def test_internal_project_no_access(internal_project):
    """Testataan sisäisen projektin hakua ilman jäsenyyttä."""
    print("Testataan sisäisen projektin hakua ilman jäsenyyttä")
    meta_data = internal_project.get_project_meta_data()
    assert meta_data is not None, "Sisäisen projektin tietojen haku pitäisi onnistua ilman jäsenyyttä"

def test_private_project_no_access(private_project_no_access):
    """Testataan yksityisen projektin hakua ilman jäsenyyttä."""
    print("Testataan yksityisen projektin hakua ilman jäsenyyttä")
    meta_data = private_project_no_access.get_project_meta_data()
    assert meta_data is None, "Yksityisen projektin tietojen haku pitäisi epäonnistua ilman jäsenyyttä"