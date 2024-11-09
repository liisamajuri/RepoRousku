import pytest
import os
from gitlab_api import ProjectData

@pytest.fixture
def valid_project():
    """
    Alustaa projektin oikealla tokenilla.
    """
    token = os.getenv("GITLAB_TOKEN", "valid_token")  # Oikea token
    url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
    return ProjectData(url, token)

def test_project_meta_data_with_valid_token(valid_project):
    """
    Testaa projektitietojen hakua oikealla tokenilla.
    """
    print("Testataan projektitietojen hakua oikealla tokenilla")
    meta_data = valid_project.get_project_meta_data()
    assert meta_data is not None, "Projektitietojen haku epäonnistui oikealla tokenilla"

def test_project_meta_data_with_invalid_token():
    """
    Testaa projektitietojen hakua virheellisellä tokenilla.
    """
    print("Testataan projektitietojen hakua virheellisellä tokenilla")
    invalid_token = "5l52t-HU2y-42y29m355F25h52"
    url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
    project = ProjectData(url, invalid_token)
    meta_data = project.get_project_meta_data()
    assert meta_data is None, "Virheellisellä tokenilla ei saatu odotettua virhettä"

def test_project_meta_data_with_expired_token():
    """
    Testaa projektitietojen hakua vanhentuneella tokenilla.
    """
    print("Testataan projektitietojen hakua vanhentuneella tokenilla")
    expired_token = "glpat-HUpy-42ye9m3oLFY5hPx"
    url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
    project = ProjectData(url, expired_token)
    meta_data = project.get_project_meta_data()
    assert meta_data is None, "Vanhentuneella tokenilla ei saatu odotettua virhettä"

def test_project_meta_data_without_token():
    """
    Testaa projektitietojen hakua ilman tokenia.
    """
    print("Testataan projektitietojen hakua ilman tokenia")
    url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"
    project = ProjectData(url, None)
    with pytest.raises(TypeError):
        project.get_project_meta_data()
        print("Odotettu virhe saavutettu ilman tokenia")
