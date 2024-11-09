import pytest
from gitlab_api import ProjectData
import libraries.components as cl

def test_project_meta_data_without_token():
    """
    Testaa, että project_meta_data palauttaa None ilman tokenia
    """
    project = ProjectData("https://gitlab.example.com/test_project", None)
    result = project.get_project_meta_data()
    assert result is None, "Odotettiin None-arvoa, kun tokenia ei ole asetettu"


def test_project_meta_data_invalid_token():
    """
    Testaa, että project_meta_data palauttaa None, kun token on virheellinen
    """
    project = ProjectData("https://gitlab.example.com/test_project", "invalid_token")
    result = project.get_project_meta_data()
    assert result is None, "Odotettiin None-arvoa, kun token on virheellinen"


def test_url_validation():
    """
    Testaa validate_url-funktion toimivuutta
    """
    valid_url = "https://gitlab.example.com/test_project"
    invalid_url = "http://invalid-url.com"
    
    assert cl.validate_url(valid_url) is True, "Valid URL ei läpäise tarkistusta"
    assert cl.validate_url(invalid_url) is False, "Virheellinen URL läpäisi tarkistuksen"
