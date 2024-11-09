import sys
import os
import webbrowser
import pytest
from gitlab_api import ProjectData
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Testidata: projektin metatiedot
test_meta_data = {
    "name": "PalikkaTestiProjekti",
    "id": 1234,
    "description": "Tämä on testiprojekti.",
    "created_at": "2024-11-01T12:00:00Z",
    "last_activity_at": "2024-11-05T12:00:00Z"
}

@pytest.fixture
def project():
    # Alustetaan ProjectData-olio
    proj = ProjectData("https://gitlab.example.com/test_project", "test_token")
    proj.project_meta_data = test_meta_data
    return proj

def test_get_name(project):
    print("Testataan projektin nimen hakemista")
    assert project.get_name() == "PalikkaTestiProjekti"

def test_get_id(project):
    print("Testataan projektin ID:n hakemista")
    assert project.get_id() == 1234

def test_get_description(project):
    print("Testataan projektin kuvauksen hakemista")
    assert project.get_description() == "Tämä on testiprojekti."

def test_get_creation_date(project):
    print("Testataan projektin luontipäivän hakemista")
    assert project.get_creation_date() == "01.11.2024"

def test_get_update_date(project):
    print("Testataan projektin päivityspäivän hakemista")
    assert project.get_update_date() == "05.11.2024"


# Avataan testiraportti selaimeen
webbrowser.open('tests/reports/report.html')