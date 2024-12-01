"""
Yksikkötestit (PalikkaPalvelut)

Tämä moduuli sisältää yksikkötestejä ProjectData- ja ClockifyData-luokille.
Testit kattavat keskeiset toiminnot, kuten projektien, milestonejen, issueiden,
committien, työtilojen ja aikakirjausten hakemisen.

Testit on toteutettu pytestin avulla, ja käytettävä data on mock-datalla
simuloitu.

Testin lopussa tarkistetaan, että HTML-raportti on luotu ja tulostetaan
linkki sen avaamiseksi selaimessa.
"""

import sys
import os
import pytest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime
from gitlab_api import ProjectData
from clockify_api import ClockifyData


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

### LOGGERIN KONFIGUROINTI ###

import logging

# Luo loggeri
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Lisää konsoli-handleri
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Määritä formatteri
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Lisää handler loggeriin
logger.addHandler(console_handler)



### GITLAB-KOMPONENTTI ###

# Testidata: projektin metatiedot ja datakomponentit
test_meta_data = {
    "name": "PalikkaTestiProjekti",
    "id": 1234,
    "description": "Tämä on testiprojekti.",
    "created_at": "2024-11-01T12:00:00Z",
    "last_activity_at": "2024-11-05T12:00:00Z",
    "namespace": {"name": "PalikkaNamespace"},
    "visibility": "private"
}

# Milestonejen testidata
today = datetime.now().date()
test_milestones_data = [
    {"iid": 1, "title": "Sprint 1", "description": "Ensimmäinen sprintti", "start_date": (today.replace(day=1) - pd.Timedelta(days=30)).isoformat(), "due_date": (today.replace(day=1) - pd.Timedelta(days=15)).isoformat(), "state": "expired"},
    {"iid": 2, "title": "Sprint 2", "description": "Toinen sprintti", "start_date": today.isoformat(), "due_date": (today + pd.Timedelta(days=15)).isoformat(), "state": "active"},
    {"iid": 3, "title": "Sprint 3", "description": "Kolmas sprintti", "start_date": (today + pd.Timedelta(days=30)).isoformat(), "due_date": (today + pd.Timedelta(days=45)).isoformat(), "state": "upcoming"}
]

# Issueiden testidata
test_issues_data = [
    {"iid": 1, "title": "Issue 1", "description": "Ensimmäinen issue", "state": "opened", "assignees": [{"id": 1, "name": "User1"}], "milestone": {"title": "Sprint 1"}, "closed_at": None},
    {"iid": 2, "title": "Issue 2", "description": "Toinen issue", "state": "closed", "assignees": [{"id": 2, "name": "User2"}], "milestone": {"title": "Sprint 2"}, "closed_at": "2024-10-10"}
]

# Committien testidata
test_commits_data = [
    {"created_at": "2024-10-01T10:00:00Z", "title": "Initial commit", "message": "Start project", "author_name": "Dev1", "committed_date": "2024-10-01"},
    {"created_at": "2024-10-15T12:00:00Z", "title": "Feature added", "message": "Add feature X", "author_name": "Dev2", "committed_date": "2024-10-15"}
]

# Branchien testidata
test_branches_data = [
    {"name": "main"},
    {"name": "dev"},
    {"name": "feature-1"}
]

# Merge requestien testidata
test_merge_requests_data = [
    {"id": 1, "title": "Merge request 1", "state": "opened"},
    {"id": 2, "title": "Merge request 2", "state": "closed"},
    {"id": 3, "title": "Merge request 3", "state": "opened"}
]

@pytest.fixture
def project():
    """
    Alustaa ProjectData-olion mock-tiedolla ja palauttaa sen testien käyttöön.
    """
    proj = ProjectData("https://gitlab.example.com/test_project", "test_token")
    proj.project_meta_data = test_meta_data
    proj.project_data = {
        "milestones": test_milestones_data,
        "issues": test_issues_data,
        "commits": test_commits_data,
        "branches": test_branches_data,
        "merge_requests": test_merge_requests_data
    }
    return proj

def test_get_name(project):
    """
    Testaa projektin nimen hakua.
    """
    print("Testataan projektin nimen hakemista")
    assert project.get_name() == "PalikkaTestiProjekti"

def test_get_id(project):
    """
    Testaa projektin ID:n hakua.
    """
    print("Testataan projektin ID:n hakemista")
    assert project.get_id() == 1234

def test_get_description(project):
    """
    Testaa projektin kuvauksen hakua.
    """
    print("Testataan projektin kuvauksen hakemista")
    assert project.get_description() == "Tämä on testiprojekti."

def test_get_creation_date(project):
    """
    Testaa projektin luontipäivän hakua ja muodon oikeellisuutta.
    """
    print("Testataan projektin luontipäivän hakemista")
    assert project.get_creation_date() == "01.11.2024"

def test_get_update_date(project):
    """
    Testaa projektin viimeisimmän päivityspäivän hakua ja muodon oikeellisuutta.
    """
    print("Testataan projektin päivityspäivän hakemista")
    assert project.get_update_date() == "05.11.2024"

def test_get_namespace_name(project):
    """
    Testaa projektin namespace-nimen hakua.
    """
    print("Testataan projektin namespace-nimen hakemista")
    assert project.get_namespace_name() == "PalikkaNamespace"

def test_get_visibility(project):
    """
    Testaa projektin näkyvyyden hakua.
    """
    print("Testataan projektin näkyvyyden hakemista")
    assert project.get_visibility() == "private"

def test_get_milestones(project):
    """
    Testaa milestone-tietojen hakua ja status-kentän oikeellisuutta jokaiselle tilalle: Päättynyt, Aktiivinen, Tuleva.
    """
    print("Testataan milestone-tietojen hakemista")
    milestones_df = project.get_milestones()
    assert isinstance(milestones_df, pd.DataFrame)
    assert len(milestones_df) == 3
    assert "status" in milestones_df.columns

    assert milestones_df["status"].iloc[0] == "Päättynyt"
    assert milestones_df["status"].iloc[1] == "Aktiivinen"
    assert milestones_df["status"].iloc[2] == "Tuleva"


def test_get_issues(project):
    """
    Testaa issue-tietojen hakua ja tarkistaa issueiden tilan sekä assignee-nimien oikeellisuuden.
    """
    print("Testataan issue-tietojen hakemista")
    issues_df = project.get_issues()
    assert isinstance(issues_df, pd.DataFrame)
    assert len(issues_df) == 2
    assert "assignees" in issues_df.columns
    assert issues_df["state"].iloc[0] == "opened"
    assert issues_df["state"].iloc[1] == "closed"

def test_get_commits(project):
    """
    Testaa commit-tietojen hakua ja tarkistaa author_name-kentän oikeellisuuden.
    """
    print("Testataan commit-tietojen hakemista")
    commits_df = project.get_commits()
    assert isinstance(commits_df, pd.DataFrame)
    assert len(commits_df) == 2
    assert "author_name" in commits_df.columns
    assert commits_df["author_name"].iloc[0] == "Dev1"

def test_count_branches(project):
    """
    Testaa branchien lukumäärän hakua.
    """
    print("Testataan branchien lukumäärän hakemista")
    assert project.count_branches() == 3  # Tarkistetaan, että haettu määrä vastaa odotettua

def test_count_open_merge_requests(project):
    """
    Testaa avoimien merge requestien lukumäärän hakua.
    """
    print("Testataan avoimien merge requestien lukumäärän hakemista")
    assert project.count_open_merge_requests() == 2  # Testataan avoimien MR:ien määrä

def test_get_assignees(project):
    """
    Testaa assignee-hakua ja varmistaa, että duplikaatit poistetaan.
    """
    print("Testataan assignee-hakua ja duplikaattien poistoa")
    assignees = project.get_assignees()
    assert isinstance(assignees, list)
    assert len(assignees) == 4
    assert "User1" in assignees and "User2" in assignees and "Dev1" in assignees and "Dev2" in assignees


### CLOCKIFY-KOMPONENTTI ###

# Testidata
test_workspaces_data = [
    {"id": "workspace1", "name": "Test Workspace 1"},
    {"id": "workspace2", "name": "Test Workspace 2"},
]

test_projects_data = [
    {"id": "project1", "name": "Test Project 1"},
    {"id": "project2", "name": "Test Project 2"},
]

test_user_hours_data = [
    {"user": "User1", "hours": 15},
    {"user": "User2", "hours": 20},
]

@pytest.fixture
def mock_clockify():
    """
    Luo mockatun ClockifyData-olion, jonka metodit palauttavat
    ennalta määriteltyä testidataa.
    """
    with patch("clockify_api.ClockifyData.__init__", return_value=None):  # Mockaa __init__
        clockify = ClockifyData()
        clockify.clockify_url = "https://mock.clockify.api/v1" 
        clockify.headers = {"X-Api-Key": "mock_api_key"}
        clockify.get_workspaces = MagicMock(return_value=test_workspaces_data)
        clockify.get_projects = MagicMock(return_value=test_projects_data)
        clockify.get_all_user_hours_df = MagicMock(return_value=pd.DataFrame(test_user_hours_data))
        return clockify
    

def test_get_workspaces(mock_clockify):
    """
    Testaa työtilojen hakemista.
    """
    workspaces = mock_clockify.get_workspaces()
    logger.debug(f"Haetut työtilat: {workspaces}")
    assert len(workspaces) == 2
    assert workspaces[0]["name"] == "Test Workspace 1"
    assert workspaces[1]["name"] == "Test Workspace 2"

def test_get_projects(mock_clockify):
    """
    Testaa projektien hakemista.
    """
    projects = mock_clockify.get_projects()
    logger.debug(f"Haetut projektit: {projects}")
    assert len(projects) == 2
    assert projects[0]["name"] == "Test Project 1"

def test_get_all_user_hours_df(mock_clockify):
    """
    Testaa käyttäjien tuntien hakemista DataFrame-muodossa.
    """
    user_hours_df = mock_clockify.get_all_user_hours_df()
    logger.debug(f"Haetut käyttäjätunnit: {user_hours_df}")
    assert len(user_hours_df) == 2
    assert user_hours_df.loc[0, "user"] == "User1"
    assert user_hours_df.loc[1, "hours"] == 20
    
    
### TESTIRAPORTTI ###    

def test_report_exists():
    """
    Testaa, että testiraportti on luotu ja tulostaa linkin raportin avaamiseksi selaimessa.
    """
    report_path = "tests/reports/unit_test_report.html"
    assert os.path.isfile(report_path), "Testiraporttia ei löytynyt!"
    print(f"Avaa testiraportti selaimessa osoitteessa: http://localhost:8010/unit_test_report.html")
