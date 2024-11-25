"""
RepoRousku API -rajapinta toteutettuna FastAPI-sovelluksena, joka tarjoaa pääsyn RepoRousku-mikropalvelun väittämään projektidataan.

Tässä tiedostossa määritellään API:n perustoiminnot ja reitit.
"""

from fastapi import FastAPI, Depends, HTTPException, Header, Query
from src.gitlab_api import ProjectData
from src.clockify_api import ClockifyData
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


### GITLAB-RAJAPINTA ###

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
async def get_gitlab_project_summary(
    project_url: str = Query(..., description="GitLab-projektin URL"),
    token: str = Header(None, alias="Authorization")
):
    """
    Hakee GitLab-projektin tilastot.

    Args:
        project_url (str): GitLab-projektin URL.
        token (str, optional): Käyttäjän syöttämä token. Oletusarvona ympäristömuuttuja.

    Returns:
        dict: Projektin tilastotiedot suunnitelman mukaisessa muodossa.
    """
    auth_token = token.replace("Bearer ", "") if token else GITLAB_TOKEN
    if not auth_token:
        raise HTTPException(status_code=401, detail="Token puuttuu!")

    try:
        # Alustetaan ProjectData-olio
        project_data = ProjectData(project_url, auth_token)

        # Haetaan projektin perustiedot
        project_id = project_data.get_id()
        name = project_data.get_name()
        namespace = project_data.get_namespace_name()
        creation_date = project_data.get_creation_date()
        update_date = project_data.get_update_date()

        # Haetaan projektin tilastot
        milestones_df = project_data.get_milestones()
        issues_df = project_data.get_issues()
        commits_count = len(project_data.get_commits())
        branches_count = project_data.count_branches()
        merge_requests_df = project_data.get_merge_requests()

        # Rakennetaan vastaus datasta
        response = {
            "project_id": project_id,
            "name": name,
            "namespace": namespace,
            "creation_date": creation_date,
            "update_date": update_date,
            "milestones": {
                "total": len(milestones_df),
                "active": len(milestones_df[milestones_df["status"] == "Aktiivinen"]) if not milestones_df.empty else 0,
                "upcoming": len(milestones_df[milestones_df["status"] == "Tuleva"]) if not milestones_df.empty else 0,
                "completed": len(milestones_df[milestones_df["status"] == "Päättynyt"]) if not milestones_df.empty else 0,
            },
            "issues": {
                "total": len(issues_df),
                "open": len(issues_df[issues_df["state"] == "opened"]) if not issues_df.empty else 0,
                "closed": len(issues_df[issues_df["state"] == "closed"]) if not issues_df.empty else 0,
            },
            "commits": commits_count,
            "branches": branches_count,
            "merge_requests": {
                "total": len(merge_requests_df),
                "open": len(merge_requests_df[merge_requests_df["state"] == "opened"]) if not merge_requests_df.empty else 0,
            },
        }

        return response

    except Exception as e:
        print(f"Error fetching project summary: {e}")
        raise HTTPException(status_code=500, detail=f"Projektin tietojen haku epäonnistui: {str(e)}")

    
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
    
    
### CLOCKIFY-RAJAPINTA ###

CLOCKIFY_URL = "https://api.clockify.me/api/v1"

@app.get("/api/v1/clockify/project-timelogs")
async def get_project_timelogs(
    workspace_id: str = Query(..., description="Clockify-työtilan ID"),
    project_id: str = Query(..., description="Clockify-projektin ID"),
    group_by_member: bool = Query(False, description="Ryhmittele jäsenittäin (oletuksena ei)"),
):
    """
    Hakee projektin aikakirjaukset.

    Args:
        workspace_id (str): Työtilan ID.
        project_id (str): Projektin ID.
        group_by_member (bool): Ryhmittely jäsenittäin (valinnainen).

    Returns:
        dict: Projektin aikakirjaukset.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        clockify.workspace_id = workspace_id

        if group_by_member:
            user_hours_df = clockify.get_all_user_hours_df(project_id)
            timelogs = user_hours_df.to_dict(orient="records") if not user_hours_df.empty else []
        else:
            total_hours = 0
            user_hours_df = clockify.get_all_user_hours_df(project_id)
            if not user_hours_df.empty:
                total_hours = user_hours_df["Työtunnit"].sum()
            timelogs = [{"total": total_hours}]

        return {
            "workspace_id": workspace_id,
            "project_id": project_id,
            "timelogs": timelogs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Projektin aikakirjausten haku epäonnistui: {str(e)}")


@app.get("/api/v1/clockify/member-timelogs")
async def get_member_timelogs(
    workspace_id: str = Query(..., description="Clockify-työtilan ID"),
    project_id: str = Query(..., description="Clockify-projektin ID"),
    user_id: str = Query(..., description="Clockify-käyttäjän ID"),
):
    """
    Hakee käyttäjän aikakirjaukset.

    Args:
        workspace_id (str): Työtilan ID.
        project_id (str): Projektin ID.
        user_id (str): Käyttäjän ID.

    Returns:
        dict: Käyttäjän aikakirjaukset.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        clockify.workspace_id = workspace_id

        time_entries_df = clockify.get_time_entries_df(user_id, project_id)
        if time_entries_df.empty:
            return {
                "workspace_id": workspace_id,
                "project_id": project_id,
                "user_id": user_id,
                "timelogs": []
            }

        timelogs = time_entries_df.to_dict(orient="records")
        total_hours = time_entries_df["duration_hours"].sum()

        return {
            "workspace_id": workspace_id,
            "project_id": project_id,
            "user_id": user_id,
            "timelogs": [{"total": total_hours}] + timelogs
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Käyttäjän aikakirjausten haku epäonnistui: {str(e)}")