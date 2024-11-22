"""
RepoRousku API -rajapinta toteutettuna FastAPI-sovelluksena, joka tarjoaa pääsyn RepoRousku-mikropalvelun väittämään projektidataan.

Tässä tiedostossa määritellään API:n perustoiminnot ja reitit.
"""

from fastapi import FastAPI, Depends, HTTPException, Header
from src.gitlab_api import ProjectData
import os
from dotenv import load_dotenv

# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()

app = FastAPI(
    title="RepoRousku API",
    description="RepoRousku API tarjoaa pääsyn RepoRousku-palvelun keräämään projektidataan, kuten GitLab- ja Clockify-tietoihin.",
    version="1.0.0"
)

# Tarkista, että ympäristömuuttujat ovat olemassa
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
CLOCKIFY_TOKEN = os.getenv("CLOCKIFY_TOKEN")

if not GITLAB_TOKEN:
    raise RuntimeError("GITLAB_TOKEN ympäristömuuttujaa ei löydy. Varmista, että .env-tiedosto on määritetty oikein.")
if not CLOCKIFY_TOKEN:
    raise RuntimeError("CLOCKIFY_TOKEN ympäristömuuttujaa ei löydy. Varmista, että .env-tiedosto on määritetty oikein.")

@app.get("/")
async def root():
    """
    API:n juuripolku.

    Returns:
        dict: Tervetuloviesti API:n käyttäjille.
    """
    return {"message": "Tervetuloa RepoRousku API:in!"}


@app.get("/health")
async def health_check():
    """
    Tarkistaa API:n toimivuuden.

    Returns:
        dict: API:n tilan ilmoittava viesti.
    """
    return {"status": "ok", "message": "Hyvä Liisa! API wörkkii oikein!"}


@app.get("/status")
async def api_status():
    """
    Palauttaa API:n nykyisen tilan.

    Returns:
        dict: Tila- ja versiotiedot.
    """
    return {
        "status": "running",
        "version": "1.0.0",
        "description": "RepoRousku API toimii oikein ja on valmis vastaanottamaan pyyntöjä."
    }

def get_gitlab_token():
    """
    Hakee GITLAB_TOKEN ympäristömuuttujasta.

    Returns:
        str: Token-arvo.

    Raises:
        HTTPException: Jos ympäristömuuttujaa ei ole asetettu.
    """
    token = os.getenv("GITLAB_TOKEN")
    if not token:
        raise HTTPException(status_code=401, detail="GITLAB_TOKEN ympäristömuuttuja puuttuu.")
    return token

@app.get("/api/v1/gitlab/project-summary")
async def get_gitlab_project_summary(project_url: str, token: str = Header(None, alias="Authorization")):
    """
    Hakee GitLab-projektin statistiikan.

    Args:
        project_url (str): GitLab-projektin URL.
        token (str, optional): Käyttäjän syöttämä token. Oletusarvona ympäristömuuttuja.

    Returns:
        dict: Projektin tilastotiedot suunnitelman mukaisessa muodossa.
    """
    auth_token = token.replace("Bearer ", "") if token else GITLAB_TOKEN
    if not auth_token:
        raise HTTPException(status_code=401, detail="Token puuttuu!")

    # Simuloitu palautus testauksen ajaksi
    project_summary = {
        "project_id": 123,
        "name": "PalikkaPalvelut",
        "namespace": "projektiopinnot",
        "creation_date": "2023-12-01",
        "update_date": "2024-01-10",
        "milestones": {
            "total": 5,
            "active": 2,
            "upcoming": 1,
            "completed": 2
        },
        "issues": {
            "total": 50,
            "open": 10,
            "closed": 40
        },
        "commits": 150,
        "branches": 3,
        "merge_requests": {
            "total": 5,
            "open": 1
        }
    }

    return project_summary

    
@app.get("/api/v1/gitlab/member-summary")
async def get_member_summary(project_url: str, member: str, token: str = Depends(get_gitlab_token)):
    print(f"Received request: project_url={project_url}, member={member}, token={token}")
    """
    Hakee tietyn jäsenen statistiikan GitLab-projektista.

    Args:
        project_url (str): GitLab-projektin URL.
        member (str): Jäsenen nimi.
        token (str): GitLab-tunnus.

    Returns:
        dict: Jäsenen tilastot, kuten commitit, issueiden tila ja merge requestit.
    """
    try:
        # Debug-tulostukset
        print(f"Debug: project_url={project_url}, member={member}, token={token}")

        # Alustetaan ProjectData-olio
        project_data = ProjectData(project_url, token)
        print("Debug: ProjectData initialized successfully.")

        # Tarkista, löytyykö jäsen projektista
        assignees = project_data.get_assignees()
        print(f"Debug: Assignees retrieved: {assignees}")
        if member not in assignees:
            return {"detail": f"Jäsentä '{member}' ei löytynyt projektista."}

        # Commit-tiedot
        commits_df, _, _ = project_data.get_commits_by_date([member], 0, 0)
        total_commits = int(commits_df.values.sum()) if not commits_df.empty else 0

        # Issue-tiedot
        closed_issues_df, _, _ = project_data.get_closed_issues_by_date([member], 0, 0)
        total_closed_issues = int(closed_issues_df.values.sum()) if not closed_issues_df.empty else 0

        open_issues_df = project_data.get_open_issues()
        open_issues = len(open_issues_df[open_issues_df["assignees"].apply(lambda x: member in x)]) if not open_issues_df.empty else 0

        # Merge request -tiedot
        merge_requests_df = project_data.get_merge_requests()
        created_mrs, reviewed_mrs = None, None

        if not merge_requests_df.empty:
            try:
                created_mrs = len(merge_requests_df[merge_requests_df["author"].apply(lambda x: x.get("name") == member)])
                reviewed_mrs = len(
                    merge_requests_df[merge_requests_df["reviewers"].apply(lambda x: member in [r.get("name") for r in x])]
                )
            except Exception as e:
                print(f"Error processing merge requests: {e}")

        # Päättele merge_requests-rakenne
        if created_mrs is None or reviewed_mrs is None:
            merge_requests = 0
        else:
            merge_requests = {
                "created": created_mrs,
                "reviewed": reviewed_mrs
            }

        # Kootaan jäsenen statistiikat
        stats = {
            "member": member,
            "issues": {
                "closed": total_closed_issues,
                "open": open_issues
            },
            "commits": total_commits,
            "merge_requests": merge_requests
        }

        print(f"Debug: Member stats compiled: {stats}")
        return stats

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=f"Jäsenen tilastojen haku epäonnistui: {str(e)}")