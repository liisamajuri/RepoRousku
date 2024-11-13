"""
Integraatiotestit (PalikkaPalvelut)

Tämä moduuli sisältää integraatiotestit GitLab-projektille. Näissä testeissä tarkastellaan sovelluksen eri 
moduulien välistä yhteistoimintaa ja tiedonsiirtoa, erityisesti käyttöliittymän ja `gitlab_api.py`:n 
välillä. Tavoitteena on varmistaa, että sovellus palauttaa ja käsittelee tiedot odotetulla tavalla, 
mukaan lukien oikean datan siirto ja formaatti eri moduulien välillä.

Huom: Integraatiotestien avulla varmistetaan, että sovelluksen eri osat toimivat saumattomasti yhdessä ja 
että tiedot siirtyvät ja muotoutuvat oikein moduulien välillä.

Testikohteet:
- Projektitietojen haku `gitlab_api.py`:n kautta ja niiden siirto käyttöliittymään.
- Kaavioiden vaatimusten mukainen tiedon käsittely.
- Dataformaattien oikeellisuus moduulien yhteydessä.

"""

import sys
sys.path.append('./src')

import pytest
import os
from gitlab_api import ProjectData
from app_pages.start import get_project_data
import pandas as pd
import streamlit as st

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
    
    # Tarkistetaan, että käyttöliittymän kautta saadaan projektitiedot oikein
    assert get_project_data(test_project_url, valid_token) is True, "Käyttöliittymän kautta haetut projektitiedot eivät onnistuneet"
    
    # Tarkistetaan, että session_state:ssa on nyt projektidata
    assert "proj_data" in st.session_state, "Projektitiedot eivät siirtyneet käyttöliittymään"
    project_data = st.session_state["proj_data"]

    # Päivitetty odotusarvo projektin nimelle
    assert project_data.get_name() == "PalikkaTesti-Small-Public", "Projektin nimi ei vastaa odotettua"
    
    print("Käyttöliittymä sai datan onnistuneesti.")


def test_data_handling_in_charts(valid_project):
    """
    Testaa, että `gitlab_api.py`:stä saadut tiedot käsitellään oikein kaavioita varten.
    """
    print("Testataan datan käsittelyä kaavioiden osalta.")

    members = ["Liisa Majuri", "Henna Mikkonen"]
    closed_issues_df = valid_project.get_data_for_closed_issues_line_chart(members)
    commits_df, date_column, pcs_column, member_column = valid_project.get_data_for_commits_line_chart(members)

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