import sys
sys.path.append('./src')

import pytest
import os
import pandas as pd
import streamlit as st
from gitlab_api import ProjectData
from app_pages.start import get_project_data

# Aseta testimuuttujat
valid_token = os.getenv("GITLAB_TOKEN")
test_project_url = "https://gitlab.dclabra.fi/palikkapalvelut/PalikkaTesti-Small-Public"

@pytest.fixture
def valid_project():
    """
    Alustaa ProjectData-olion oikealla tokenilla ja testiprojektin URL:llä.
    """
    return ProjectData(test_project_url, valid_token)

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
    assert get_project_data(test_project_url, valid_token) is True, "Käyttöliittymän kautta haetut projektitiedot eivät onnistuneet"
    
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
    closed_issues_df = valid_project.get_closed_issues_by_date(members)
    commits_df, date_column, pcs_column, member_column = valid_project.get_commits_by_date(members)

    assert isinstance(closed_issues_df, pd.DataFrame), "Suljettujen issueiden data ei palauttanut DataFramea"
    assert isinstance(commits_df, pd.DataFrame), "Commiteiden data ei palauttanut DataFramea"

    print("Datan käsittely kaavioita varten onnistui.")

def test_report_exists():
    """
    Testaa, että testiraportti on luotu ja tulostaa linkin raportin avaamiseksi selaimessa.
    """
    report_path = "tests/reports/integration_test_report.html"
    assert os.path.isfile(report_path), "Testiraporttia ei löytynyt!"
    print(f"Avaa testiraportti selaimessa osoitteessa: http://localhost:8010/integration_test_report.html")
