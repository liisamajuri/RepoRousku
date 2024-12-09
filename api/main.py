"""
RepoRousku API -rajapinta toteutettuna FastAPI-sovelluksena, joka tarjoaa pääsyn RepoRousku-mikropalvelun väittämään projektidataan.

Tässä tiedostossa määritellään API:n perustoiminnot ja reitit.
"""
import sys
import os
import logging

# Lisää src-kansio Pythonin hakupolkuun
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))



from fastapi import FastAPI, Depends, HTTPException, Header, Query
from src.gitlab_api import ProjectData
from src.clockify_api import ClockifyData
from typing import Optional
from dotenv import load_dotenv
from fastapi.responses import JSONResponse


# Lataa ympäristömuuttujat .env-tiedostosta
load_dotenv()


# Loggerin asetukset
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("RepoRouskuAPI")

app = FastAPI(
    title="RepoRousku API",
    description="RepoRousku API tarjoaa pääsyn RepoRousku-palvelun keräämään projektidataan, kuten GitLab- ja Clockify-tietoihin.",
    version="1.0.0",
    docs_url="/docs",  # Swagger-UI:n oletuspolku
    redoc_url="/redoc",  # ReDoc-dokumentaation polku
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
    logger.debug("Käyttäjä pyysi juuripolkua.")
    return {"message": "Tervetuloa RepoRousku API:in!"}


@app.get("/health")
async def health_check():
    """
    Tarkistaa API:n toimivuuden.

    Returns:
        dict: API:n tilan ilmoittava viesti.
    """
    logger.debug("Käyttäjä pyysi health-checkiä.")
    return {"status": "ok", "message": "Hyvä Liisa! API wörkkii oikein!"}


@app.get("/status")
async def api_status():
    """
    Palauttaa API:n nykyisen tilan.

    Returns:
        dict: Tila- ja versiotiedot.
    """
    logger.debug("Käyttäjä pyysi API:n status-endpointtia.")
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

def get_id_from_name_if_needed(clockify, workspace_name=None, project_name=None, user_name=None):
    """
    Hakee ID:n, jos syöte on nimi (muuten käyttää suoraan ID:tä).
    """
    # Hakee workspace ID:n, jos syötteenä on nimi
    if workspace_name and not workspace_name.isdigit():
        workspace_id = clockify.get_workspace_id_by_name(workspace_name)
    else:
        workspace_id = workspace_name
    
    # Hakee project ID:n, jos syötteenä on nimi
    if project_name and not project_name.isdigit():
        project_id = clockify.get_project_id_by_name(workspace_id, project_name)
    else:
        project_id = project_name
    
    # Hakee user ID:n, jos syötteenä on nimi
    if user_name and not user_name.isdigit():
        user_id = clockify.get_user_id_by_name(workspace_id, user_name)
    else:
        user_id = user_name
    
    return workspace_id, project_id, user_id




@app.get("/api/v1/clockify/workspaces")
async def get_workspaces():
    """
    Palauttaa kaikki saatavilla olevat työtilat.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        workspaces = clockify.get_workspaces()
        return {"workspaces": workspaces}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Työtilojen haku epäonnistui: {str(e)}")


@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects")
async def get_projects(workspace_id: str):
    """
    Palauttaa kaikki projektit annetusta työtilasta.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        
        # Muunna työtilan nimi ID:ksi tarvittaessa
        workspace_id, _, _ = get_id_from_name_if_needed(
            clockify, 
            workspace_name=workspace_id
        )

        clockify.workspace_id = workspace_id
        projects = clockify.get_projects()
        if not projects:
            return {"projects": [], "message": "Ei löytynyt projekteja annetusta työtilasta."}
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Projektien haku epäonnistui: {str(e)}")


@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/users")
async def get_users_and_hours(workspace_id: str, project_id: str):
    """
    Palauttaa kaikkien projektin käyttäjien tunnit annetusta työtilasta.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        
        # Muunna nimet ID:iksi tarvittaessa
        workspace_id, project_id, _ = get_id_from_name_if_needed(
            clockify, 
            workspace_name=workspace_id, 
            project_name=project_id
        )
        
        clockify.workspace_id = workspace_id
        clockify.project_id = project_id
        user_hours_df = clockify.get_all_user_hours_df()
        if user_hours_df.empty:
            return {"users": [], "message": "Ei löytynyt tunnitietoja käyttäjille projektissa."}
        # Palauta tulokset JSON-muodossa
        return JSONResponse(content=user_hours_df.to_dict(orient="records"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Käyttäjätuntien haku epäonnistui: {str(e)}")



@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/users/{user_id}/time-entries")
async def get_time_entries(workspace_id: str, project_id: str, user_id: str):
    """
    Palauttaa yksittäisen käyttäjän aikakirjaukset projektista.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        
        # Muunna nimet ID:iksi tarvittaessa
        workspace_id, project_id, user_id = get_id_from_name_if_needed(
            clockify, 
            workspace_name=workspace_id, 
            project_name=project_id, 
            user_name=user_id
        )
        
        # Aseta ID:t ClockifyData-objektiin
        clockify.workspace_id = workspace_id
        clockify.project_id = project_id
        # Hae aikakirjaukset
        time_entries_df = clockify.get_time_entries_df(user_id, project_id)
        if time_entries_df.empty:
            return {"time_entries": [], "message": "Ei löytynyt aikakirjauksia käyttäjälle projektissa."}
        # Palauta tulokset JSON-muodossa
        return JSONResponse(content=time_entries_df.to_dict(orient="records"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aikakirjausten haku epäonnistui: {str(e)}")

    
@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/total-hours")
async def get_project_total_hours(workspace_id: str, project_id: str):
    """
    Palauttaa projektin kokonaistunnit työtilassa.
    """
    try:
        clockify = ClockifyData(CLOCKIFY_URL)
        
        # Muunna nimet ID:iksi tarvittaessa
        workspace_id, project_id, _ = get_id_from_name_if_needed(clockify, workspace_name=workspace_id, project_name=project_id)
        
        clockify.workspace_id = workspace_id
        clockify.project_id = project_id
        
        # Hae kaikkien käyttäjien tunnit
        user_hours_df = clockify.get_all_user_hours_df()
        
        # Laske projektin kokonaistunnit
        total_hours = user_hours_df["Työtunnit"].sum() if not user_hours_df.empty else 0
        
        return {"project_id": project_id, "total_hours": total_hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Projektin kokonaistuntien haku epäonnistui: {str(e)}")


    
    
@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/users/{user_id}/total-hours")
async def get_user_total_hours(workspace_id: str, project_id: str, user_id: str):
    """
    Palauttaa käyttäjän kokonaistunnit projektissa.
    """
    try:
        # Muutetaan nimistä ID:t tarvittaessa
        clockify = ClockifyData(CLOCKIFY_URL)
        workspace_id, project_id, user_id = get_id_from_name_if_needed(clockify, workspace_id, project_id, user_id)
        
        # Käsitellään Clockify API:lla
        
        clockify.workspace_id = workspace_id
        clockify.project_id = project_id
        time_entries_df = clockify.get_time_entries_df(user_id, project_id)
        total_hours = time_entries_df["duration_hours"].sum() if not time_entries_df.empty else 0
        return {"user_id": user_id, "project_id": project_id, "total_hours": total_hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Käyttäjän kokonaistuntien haku epäonnistui: {str(e)}")

@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/sprint-hours")
async def get_sprint_hours(
    workspace_id: str,
    project_id: str,
    gitlab_url: str = Query(..., description="GitLab-projektin URL"),
    token: str = Header(None, alias="Authorization"),
):
    """
    Palauttaa käyttäjien sprinttikohtaiset tunnit GitLabin milestonejen perusteella.
    """
    # Käsitellään GitLab-token
    gitlab_token = token.replace("Bearer ", "") if token else GITLAB_TOKEN
    if not gitlab_token:
        raise HTTPException(status_code=401, detail="GitLab-token puuttuu!")

    try:
        clockify = ClockifyData(CLOCKIFY_URL)

        # Muunna nimet ID:ksi tarvittaessa
        workspace_id, project_id, _ = get_id_from_name_if_needed(
            clockify,
            workspace_name=workspace_id,
            project_name=project_id,
        )

    
        clockify.workspace_id = workspace_id
        clockify.project_id = project_id

        # Hae sprinttikohtaiset tunnit ClockifyData-luokalla
        sprint_hours_df = clockify.get_sprint_hours(gitlab_url, gitlab_token)
        if sprint_hours_df.empty:
            return {
                "sprint_hours": [],
                "message": "Ei löytynyt sprinttikohtaisia tietoja annetulle projektille ja työtilalle.",
            }
        # Palauta tulokset JSON-muodossa
        return JSONResponse(sprint_hours_df.to_dict(orient="records"))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Sprinttituntien haku epäonnistui: {str(e)}",
        )

@app.get("/api/v1/clockify/workspaces/{workspace_id}/projects/{project_id}/tag-hours")
async def get_tag_hours(
    workspace_id: str,
    project_id: str,
    user_names: Optional[str] = Query(None, description="Pilkuilla eroteltu lista käyttäjän nimistä, joille tunnit haetaan.")
):
    """
    Palauttaa projektin työtunnit tageittain. Tukee käyttäjien nimien tai kaikkien käyttäjien hakemista.

    Args:
        workspace_id (str): Clockify-työtilan ID tai nimi.
        project_id (str): Clockify-projektin ID tai nimi.
        user_names (str, optional): Käyttäjänimet pilkuilla eroteltuna. Oletuksena hakee kaikille käyttäjille.
    """
    try:
        # ClockifyData-objekti
        clockify = ClockifyData(CLOCKIFY_URL)

        # Muunna nimet ID:ksi tarvittaessa
        workspace_id, project_id, _ = get_id_from_name_if_needed(
            clockify, workspace_name=workspace_id, project_name=project_id
        )
        clockify.workspace_id = workspace_id

        # Käyttäjien ID:t nimien perusteella, jos käyttäjänimiä annetaan
        if not user_names:  # Tämä tarkistaa, onko user_names None tai tyhjä
            users_in_workspace = clockify.get_users_in_workspace()
            if not users_in_workspace:
                raise ValueError("Ei löytynyt työtilan käyttäjiä.")
            user_ids = [user["id"] for user in users_in_workspace]
        else:
            # Käyttäjänimet tai ID:t, jaetaan ne pilkuilla ja käsitellään erikseen
            user_names_or_ids = user_names.split(",")
            user_ids = []
            for item in user_names_or_ids:
                item = item.strip()
                if item.isdigit():  # Jos se on numero, se on ID
                    user_ids.append(item)
                else:  # Jos se ei ole numero, se käsitellään käyttäjänimenä
                    user_id = clockify.get_user_id_by_name(workspace_id, item)
                    if user_id:  # Varmistetaan, että user_id ei ole None
                        user_ids.append(user_id)
                    else:
                        raise ValueError(f"Käyttäjänimi '{item}' ei ole kelvollinen.")
                
            # Jos user_ids on tyhjä, se ei voi jatkua
            if not user_ids:
                raise ValueError("Ei löytynyt kelvollisia käyttäjiä.")
        
        # Debug: tulosta käyttäjä-ID:t ennen tagi-tuntien hakua
        print(f"User IDs: {user_ids}")

        # Hae projektin tagikohtaiset tunnit
        tag_hours_df = clockify.get_project_tag_hours(project_id, user_ids)

        # Tarkistetaan, ettei tag_hours_df ole None tai tyhjä
        if tag_hours_df is None or tag_hours_df.empty:
            return {"tag_hours": [], "message": "Ei löytynyt tunnitietoja."}

        # Käydään läpi kaikki tagit ja poistetaan tyhjät tagit
        tag_hours = []
        for tag in tag_hours_df.to_dict(orient="records"):
            if tag.get("tag") is not None:  # Varmistetaan, että tag ei ole None
                tag_hours.append(tag)
        
        # Palautetaan tagit 
        return JSONResponse({
            "tag_hours": tag_hours,
        })
    
    except Exception as e:
        print(f"Virhe: {str(e)}")  # Debugging virheilmoitusta varten
        raise HTTPException(status_code=500, detail=f"Tagien tuntien haku epäonnistui: {str(e)}")


