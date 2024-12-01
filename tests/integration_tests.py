"""
Integraatiotestit (PalikkaPalvelut)

Tämä moduuli sisältää integraatiotestit, joissa testataan PalikkaPalvelut-sovelluksen komponenttien yhteistoimintaa.
Testit varmistavat, että käyttöliittymä voi hakea ja käsitellä dataa taustajärjestelmistä (GitLab ja Clockify) ja että
nämä tiedot esitetään sovelluksessa oikein.

Integraatiotestit tarkastelevat mm. seuraavia skenaarioita:
1. GitLab-projektin tietojen haku ja käsittely.
2. Clockify-datan haku ja siirtäminen käyttöliittymän tilaan (`session_state`).
3. Datan käsittely kaavioita varten.
4. Testiraportin luonti.

"""

import sys
sys.path.append('./src')

import pytest
import os
import pandas as pd
import streamlit as st
from gitlab_api import ProjectData
from clockify_api import ClockifyData
from app_pages.start import get_project_data, fetch_clockify_data
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
    #monkeypatch.setenv("GITLAB_TOKEN", MOCK_GITLAB_TOKEN)



### GITLAB-KOMPONENTTI ###

# Aseta testimuuttujat
valid_gitlab_token = os.getenv("GITLAB_TOKEN")
    
test_project_url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"

@pytest.fixture
def valid_project():
    """
    Alustaa ProjectData-olion oikealla tokenilla ja testiprojektin URL:llä.
    """
    return ProjectData(test_project_url, valid_gitlab_token)

def test_project_data_retrieval_and_formatting(valid_project):
    """
    Testaa projektitietojen hakua ja varmistaa, että data palautetaan oikeassa muodossa.
    """
    print("Testataan projektitietojen hakua ja oikeaa dataformaattia.")
    
    milestones_df = valid_project.get_milestones()
    issues_df = valid_project.get_issues()
    commits_df = valid_project.get_commits()

    assert isinstance(milestones_df, pd.DataFrame), "Milestonet eivät palauttaneet DataFramea"
    assert isinstance(issues_df, pd.DataFrame), "Issuet eivät palauttaneet DataFramea"
    assert isinstance(commits_df, pd.DataFrame), "Commitit eivät palauttaneet DataFramea"

    print("Kaikki projektitiedot haettu ja palautettu oikeassa muodossa.")

def test_data_flow_to_interface(valid_project):
    """
    Testaa, että käyttöliittymä saa tiedot oikein `gitlab_api.py`:stä `get_project_data`-funktion kautta.
    """
    print("Testataan datan siirtymistä käyttöliittymälle.")
    
    # Alusta session state
    proj_data = "proj_data"

    if proj_data not in st.session_state:
        st.session_state[proj_data] = None

    # Simuloi käyttöliittymän tietojen hakua
    assert get_project_data(test_project_url, valid_gitlab_token) is True, "Käyttöliittymän kautta haetut projektitiedot eivät onnistuneet"
    
    # Tarkista, että session state sisältää projektidatan
    assert proj_data in st.session_state, "Projektitiedot eivät siirtyneet käyttöliittymään"
    project_data = st.session_state[proj_data]

    # Varmista, että projektin nimi on odotettu
    assert project_data.get_name() == "PalikkaTesti-Small-Public", "Projektin nimi ei vastaa odotettua"
    print("Käyttöliittymä sai datan onnistuneesti.")

def test_data_handling_in_charts(valid_project):
    """
    Testaa, että `gitlab_api.py`:stä saadut tiedot käsitellään oikein kaavioita varten.
    """
    print("Testataan datan käsittelyä kaavioiden osalta.")

    members = ["Liisa Majuri", "Henna Mikkonen"]
    closed_issues_df, dummy1, dummy2 = valid_project.get_closed_issues_by_date(members, 0, 0)
    commits_df, date_column, pcs_column = valid_project.get_commits_by_date(members, 0, 0)

    assert isinstance(closed_issues_df, pd.DataFrame), "Suljettujen issueiden data ei palauttanut DataFramea"
    assert isinstance(commits_df, pd.DataFrame), "Commiteiden data ei palauttanut DataFramea"

    print("Datan käsittely kaavioita varten onnistui.")


    
    
### CLOCKIFY-KOMPONENTTI ###

# Aseta testimuuttujat

valid_clockify_token = MOCK_CLOCKIFY_TOKEN

clockify_url = "https://api.clockify.me/api/v1"
valid_workspace_id = "671fabab605d557fc5342652"
valid_project_id = "671fac534ce4600d320d577d"


@pytest.fixture
def valid_clockify():
    """
    Palauttaa ClockifyData-olion oikealla tokenilla.
    """
    print("Testataan Clockify-olion luontia.")
    if not valid_clockify_token:
        raise ValueError("CLOCKIFY_TOKEN ympäristömuuttujaa ei ole asetettu!")
    return ClockifyData(clockify_url=clockify_url, api_key=valid_clockify_token)


def test_clockify_data_retrieval_and_formatting(valid_clockify):
    """
    Testaa Clockify-datan hakua ja varmistaa, että data palautetaan oikeassa muodossa.
    """
    print("Testataan Clockify-datan hakua ja oikeaa dataformaattia.")
    
    workspaces = valid_clockify.get_workspaces()
    valid_clockify.workspace_id = valid_workspace_id
    projects = valid_clockify.get_projects()
    all_user_hours_df = valid_clockify.get_all_user_hours_df()

    assert isinstance(workspaces, list), "Työtilat eivät palauttaneet listaa"
    assert isinstance(projects, list), "Projektit eivät palauttaneet listaa"
    assert isinstance(all_user_hours_df, pd.DataFrame), "Käyttäjien tuntidata ei palauttanut DataFramea"

    print("Kaikki Clockify-data haettu ja palautettu oikeassa muodossa.")
    

def test_fetch_clockify_data(valid_clockify):
    """
    Testaa `fetch_clockify_data`-funktion toimintaa mockatuilla Streamlit-komponenteilla ja Clockify-tiedoilla.
    """
    print("Testataan Clockify-datan hakua käyttöliittymässä...")
    
    # Mockataan Streamlitin selectbox ja Clockify API -kutsut
    with patch("streamlit.selectbox", side_effect=lambda label, options: options[0]), \
         patch.object(valid_clockify, "get_workspaces", return_value=[{"name": "Palikkapalvelut", "id": valid_workspace_id}]), \
         patch.object(valid_clockify, "get_projects", return_value=[{"name": "Project-4", "id": valid_project_id}]), \
         patch.object(valid_clockify, "get_all_user_hours_df", return_value=pd.DataFrame({"User": ["Test User"], "Hours": [10]})):
    
        result_df = fetch_clockify_data(valid_clockify)

        assert result_df is not None, "Clockify-datan haku epäonnistui."
        assert "clockify_data" in st.session_state, "Clockify-dataa ei tallennettu session_stateen."
        assert st.session_state["clockify_workspace"] == valid_workspace_id, "Työtila ID ei tallennettu oikein."
        assert st.session_state["clockify_project"] == valid_project_id, "Projektin ID ei tallennettu oikein."
        
        print("Clockify-datan haku käyttöliittymässä onnistui.")
    

def test_clockify_data_handling_in_charts(valid_clockify):
    """
    Testaa, että Clockify-datan käsittely onnistuu kaavioita varten.
    """
    print("Testataan Clockify-datan käsittelyä kaavioiden osalta.")

    valid_clockify.workspace_id = valid_workspace_id
    valid_clockify.project_id = valid_project_id

    sprint_hours_df = valid_clockify.get_all_user_hours_df()

    assert isinstance(sprint_hours_df, pd.DataFrame), "Sprinttien tuntidata ei palauttanut DataFramea"

    print("Clockify-datan käsittely kaavioita varten onnistui.")


### TESTIRAPORTTI ###

def test_report_exists():
    """
    Testaa, että testiraportti on luotu ja tulostaa linkin raportin avaamiseksi selaimessa.
    """
    report_path = "tests/reports/integration_test_report.html"
    assert os.path.isfile(report_path), "Testiraporttia ei löytynyt!"
    print(f"Avaa testiraportti selaimessa osoitteessa: http://localhost:8010/integration_test_report.html")