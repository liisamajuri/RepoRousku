"""
RepoRouskun rajapinta, joka hakee tiedot Clockifyn APIsta.
Sisältää ClockifyData-luokan, joka kapseloi työtuntitiedot ja tarjoaa 
palveluinaan pureskeltua dataa käyttöliittymää varten.
"""

import requests
import os
import re
import pandas as pd
from gitlab_api import ProjectData
import pytz 



class ClockifyData:
    """
    Luokka Clockifyn tietojen hakemiseen ja käsittelyyn.
    """
    def __init__(self, clockify_url, api_key=None):
        self.clockify_url = clockify_url
        self.workspace_id = None
        self.project_id = None
        self.user_id = None
        self.api_key = api_key or os.getenv("CLOCKIFY_TOKEN")
        self.headers = {"X-Api-Key": self.api_key}

        if not self.api_key:
            raise ValueError("CLOCKIFY_TOKEN ympäristömuuttujaa ei ole asetettu!")

        self.init(clockify_url)

    def init(self, clockify_url):
        """
        Luokan alustus.
        """
        self.clockify_url = clockify_url
        self.get_workspaces()

    def _get(self, endpoint):
        """ Apufunktio GET-pyyntöjen tekemiseen Clockify-APIin. """
        url = f"{self.clockify_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise Exception(f"API-pyyntö epäonnistui: {response.status_code} - {response.text}")
        return response.json()
    
    def iso_duration_to_seconds(self, duration):
        """Muuntaa ISO 8601 -kestoarvon sekunneiksi."""
        if duration is None:
            return 0  # Palautetaan 0, jos duration on None

        hours = minutes = seconds = 0
        match = re.match(r"PT(\d+)H(\d+)M(\d+)S", duration)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = int(match.group(3))
        else:
            match_hours = re.match(r"PT(\d+)H", duration)
            match_minutes = re.match(r"PT(\d+)M", duration)
            match_seconds = re.match(r"PT(\d+)S", duration)

            if match_hours:
                hours = int(match_hours.group(1))
            if match_minutes:
                minutes = int(match_minutes.group(1))
            if match_seconds:
                seconds = int(match_seconds.group(1))

        return hours * 3600 + minutes * 60 + seconds

    def get_workspaces(self):
        """
        Hakee Clockifyn workspacet
        """
        response = requests.get(f"{self.clockify_url}/workspaces", headers=self.headers)
        if response.status_code == 200:
            workspaces = response.json()
            self.workspace_id = workspaces[0]["id"] if workspaces else None
            return workspaces
        else:
            print(f"Virhe haettaessa työtiloja: {response.status_code}")
            return []

    def get_projects(self):
        """
        Hakee workspacen projektit
        """
        if not self.workspace_id:
            print("Työtilan ID ei ole asetettu.")
            return []

        response = requests.get(f"{self.clockify_url}/workspaces/{self.workspace_id}/projects", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Virhe haettaessa projekteja: {response.status_code}")
            return []

    def get_users_in_workspace(self):
        """
        Hakee workspacen käyttäjät
        """
        if not self.workspace_id:
            print("Työtilan ID ei ole asetettu.")
            return []

        response = requests.get(f"{self.clockify_url}/workspaces/{self.workspace_id}/users", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Virhe haettaessa käyttäjiä: {response.status_code}")
            return []

    def get_workspace_id_by_name(self, workspace_name):
        """ Hakee työtilan ID:n nimen perusteella. """
        workspaces = self.get_workspaces()
        for workspace in workspaces:
            if workspace['name'].lower() == workspace_name.lower():
                return workspace['id']
        raise Exception(f"Työtilaa '{workspace_name}' ei löytynyt.")

    def get_project_id_by_name(self, workspace_id, project_name):
        """ Hakee projektin ID:n nimen perusteella. """
        projects = self._get(f"workspaces/{workspace_id}/projects")
        for project in projects:
            if project['name'].lower() == project_name.lower():
                return project['id']
        raise Exception(f"Projektia '{project_name}' ei löytynyt työtilasta.")

    def get_user_id_by_name(self, workspace_id, user_name):
        """ Hakee käyttäjän ID:n nimen perusteella. """
        users = self._get(f"workspaces/{workspace_id}/users")
        for user in users:
            if user['name'].lower() == user_name.lower():
                return user['id']
        raise Exception(f"Käyttäjää '{user_name}' ei löytynyt työtilasta.")

    def get_time_entries_df(self, user_id, project_id):
        """
        Hakee käyttäjän työtunnit tietyssä projektissa ja palauttaa ne DataFrame-muodossa.
        """
        if not self.workspace_id:
            print("Työtilan ID ei ole asetettu.")
            return pd.DataFrame()

        url = f"{self.clockify_url}/workspaces/{self.workspace_id}/user/{user_id}/time-entries?project={project_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            time_entries = response.json()
            data = []

            for entry in time_entries:
                if "timeInterval" in entry:
                    start_time = entry["timeInterval"].get("start")
                    end_time = entry["timeInterval"].get("end")
                    duration = entry["timeInterval"].get("duration")
                    seconds = self.iso_duration_to_seconds(duration)
                    hours = seconds / 3600
                    
                    
                    data.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_seconds": seconds,
                        "duration_hours": hours  
                    })

            
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Virhe haettaessa aikakirjauksia käyttäjälle {user_id}: {response.status_code}")
            return pd.DataFrame()
        
    def get_all_user_hours_df(self):
        """
        Hakee kaikkien käyttäjien työtunnit ja palauttaa ne yhdistettynä DataFrame-muodossa.
        """
        users_in_workspace = self.get_users_in_workspace()
        all_user_hours = []

        for user in users_in_workspace:
            user_id = user["id"]
            time_entries_df = self.get_time_entries_df(user_id, self.project_id)
            if not time_entries_df.empty:
                total_hours = time_entries_df['duration_hours'].sum()
                all_user_hours.append({
                    "Nimi": user.get("name", "Tuntematon käyttäjä"),  
                    "Työtunnit": total_hours
                })

    
        return pd.DataFrame(all_user_hours)


    def get_sprint_hours(self, gitlab_url, gitlab_token):
        """
        Hakee kaikkien käyttäjien työtunnit milestoneittain ja palauttaa ne yhdistettynä DataFrame-muodossa.
        """
        gitlab_project = ProjectData(gitlab_url, gitlab_token)
        milestones = gitlab_project.get_milestones()

        if milestones.empty:
            return pd.DataFrame()

        sprint_hours = []
        users_in_workspace = self.get_users_in_workspace()

        for _, milestone in milestones.iterrows():
            milestone_name = milestone['title']
            start_date = pd.Timestamp(milestone['start_date']).replace(hour=0, minute=0, second=0, tzinfo=pytz.UTC)
            end_date = pd.Timestamp(milestone['due_date']).replace(hour=23, minute=59, second=59, tzinfo=pytz.UTC)

            for user in users_in_workspace:
                user_id = user["id"]
                time_entries_df = self.get_time_entries_df(user_id, self.project_id)
                if not time_entries_df.empty:
                    time_entries_df['start_time'] = pd.to_datetime(time_entries_df['start_time'], format="%Y-%m-%dT%H:%M:%SZ").dt.tz_localize('UTC')
                    time_entries_df['duration_hours'] = time_entries_df['duration_seconds'] / 3600
                    sprint_entries = time_entries_df[
                        (time_entries_df['start_time'] >= start_date) & 
                        (time_entries_df['start_time'] <= end_date)
                    ]
                    total_hours = sprint_entries['duration_hours'].sum()

                    sprint_hours.append({
                        "user": user["name"],
                        "milestone": milestone_name,
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_hours": total_hours
                    })

        sprint_hours_df = pd.DataFrame(sprint_hours)

        if not sprint_hours_df.empty:
            # Group by user and milestone, summing the total hours worked
            sprint_hours_df_grouped = sprint_hours_df.groupby(['user', 'milestone']).agg({'total_hours': 'sum'}).reset_index()
            return sprint_hours_df_grouped
    
        return pd.DataFrame()


    def get_tags(self):
        """
        Hakee tagit ja palauttaa ne listana.
        """
        if not self.workspace_id:
            print("Työtilan ID ei ole asetettu.")
            return []
        response = requests.get(f"{self.clockify_url}/workspaces/{self.workspace_id}/tags", headers=self.headers)
        print("get_tags response JSON:", response.json())

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Virhe haettaessa tageja: {response.status_code}")
            return []


    def get_project_tag_hours(self, project_id, user_ids):
        """
        Hakee projektin kaikki tagit, aikakirjaukset ja laskee tunnit tageittain useille käyttäjille.

        Args:
            project_id (str): Clockify-projektin ID.
            user_ids (list): Lista Clockify-käyttäjien ID:istä.

        Returns:
            (DataFrame): DataFrame, joka sisältää tagin nimen ja siihen liittyvät tunnit kaikille käyttäjille.
        """
        if not self.workspace_id:
            raise ValueError("Työtilan ID ei ole asetettu.")

        tags = self.get_tags()
        if not tags:
            print("Ei löytynyt tageja.")
            return pd.DataFrame()

        users_in_workspace = self.get_users_in_workspace()

        tag_hours_list = []

        for user_id in user_ids:
            
            user = next((user for user in users_in_workspace if user["id"] == user_id), None)
            if user is None:
                print(f"Käyttäjää {user_id} ei löytynyt työtilasta.")
                continue  
            url = f"{self.clockify_url}/workspaces/{self.workspace_id}/user/{user_id}/time-entries?project={project_id}"
            response = requests.get(url, headers=self.headers)
            if response.status_code == 404:
                print(f"Projektia ei löydy ID:llä {project_id} käyttäjältä {user_id}.")
                continue
            elif response.status_code != 200:
                print(f"Virhe haettaessa aikakirjauksia projektista {project_id} käyttäjältä {user_id}: {response.status_code}")
                continue
            time_entries = response.json()
            for tag in tags:
                tag_id = tag["id"]
                tag_name = tag["name"]
                tagged_entries = [
                    entry for entry in time_entries
                    if "tagIds" in entry and isinstance(entry["tagIds"], list) and tag_id in entry["tagIds"]
                ]
                total_hours = sum(
                    self.iso_duration_to_seconds(entry["timeInterval"].get("duration", "PT0S")) / 3600
                    for entry in tagged_entries
                )
                tag_hours_list.append({"user_id": user_id, "user_name": user["name"], "tag": tag_name, "total_hours": total_hours})
        return pd.DataFrame(tag_hours_list)


    def get_tag_hours(self):
        """Hakee ja laskee työtunnit kullekin tagille työtilassa."""
        tag_hours_list = []

        tags = self.get_tags()
        if not tags:
            print("Ei löytynyt tageja.")
            return pd.DataFrame()
        for tag in tags:
            tag_id = tag["id"]
            tag_name = tag["name"]
            print(f"Käsitellään tagi: {tag_name}, ID: {tag_id}")
            time_entries_df = self.get_time_entries_by_tag(tag_ids=[tag_id])
            if not time_entries_df.empty:
                total_tag_hours = time_entries_df['duration_hours'].sum()
                print(f"Tagille {tag_name} kokonaistunnit: {total_tag_hours}")
                tag_hours_list.append({
                    "tag": tag_name,
                    "total_hours": total_tag_hours
                })
            else:
                print(f"Ei aikakirjauksia tagille {tag_name}")
        if tag_hours_list:
            tag_hours_df = pd.DataFrame(tag_hours_list)
            print(f"Tag Hours List: {tag_hours_df}")
            return tag_hours_df
        else:
            return pd.DataFrame()


    def get_project_tag_and_sprint_hours(self, gitlab_url, gitlab_token):
        """
        Hakee projektin tagit, aikakirjaukset, sprintit ja laskee tunnit sekä tageittain että sprintittäin käyttäjille.
        """
        if not self.workspace_id:
            raise ValueError("Työtilan ID ei ole asetettu.")

        tags = self.get_tags()
        if not tags:
            print("Ei löytynyt tageja.")
            return pd.DataFrame()

        gitlab_project = ProjectData(gitlab_url, gitlab_token)
        milestones = gitlab_project.get_milestones()

        if milestones.empty:
            print("Ei löytynyt sprints-milestoneja.")
            return pd.DataFrame()

        users_in_workspace = self.get_users_in_workspace()

        tag_and_sprint_hours_list = []

        for user in users_in_workspace:
            user_id = user["id"]
            user_name = user["name"]

            url = f"{self.clockify_url}/workspaces/{self.workspace_id}/user/{user_id}/time-entries"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 404:
                print(f"Aikakirjauksia ei löydy käyttäjältä {user_id}.")
                continue
            elif response.status_code != 200:
                print(f"Virhe haettaessa aikakirjauksia käyttäjältä {user_id}: {response.status_code}")
                continue

            try:
                time_entries = response.json()
            except ValueError:
                print(f"Virhe käsiteltäessä JSON-vastausta käyttäjältä {user_id}.")
                continue
            for _, milestone in milestones.iterrows():
                milestone_name = milestone['title']
                start_date = pd.Timestamp(milestone['start_date']).replace(hour=0, minute=0, second=0, tzinfo=pytz.UTC)
                end_date = pd.Timestamp(milestone['due_date']).replace(hour=23, minute=59, second=59, tzinfo=pytz.UTC)

                sprint_entries = [
                    entry for entry in time_entries
                    if "timeInterval" in entry and 
                    start_date <= pd.to_datetime(entry["timeInterval"]["start"]) <= end_date
                ]
                sprint_total_hours = sum(
                    self.iso_duration_to_seconds(entry["timeInterval"].get("duration", "PT0S")) / 3600
                    for entry in sprint_entries
                )

                for tag in tags:
                    tag_id = tag["id"]
                    tag_name = tag["name"]
                    tagged_entries = [
                        entry for entry in sprint_entries
                        if entry.get("tagIds") and tag_id in entry["tagIds"]
                    ]


                    tag_total_hours = sum(
                        self.iso_duration_to_seconds(entry["timeInterval"].get("duration", "PT0S")) / 3600
                        for entry in tagged_entries
                    )

                    tag_and_sprint_hours_list.append({
                        "user_id": user_id,
                        "user_name": user_name,
                        "tag": tag_name,
                        "milestone": milestone_name,
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_tag_hours": tag_total_hours,
                        "total_sprint_hours": sprint_total_hours
                    })
        return pd.DataFrame(tag_and_sprint_hours_list)
    
    def get_project_task_hours(self):
        """ Hae taskit ja niiden tunnit projektista
        """
        if not self.workspace_id or not self.project_id:
            raise ValueError("Workspace ID tai Project ID puuttuu.")
        
        url = f"{self.base_url}/workspaces/{self.workspace_id}/projects/{self.project_id}/tasks"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        tasks = response.json()

        task_data = []
        for task in tasks:
            duration_str = task.get("duration", "PT0S") 
            hours, minutes = 0, 0
            if "H" in duration_str:
                hours = int(duration_str.split("H")[0].replace("PT", ""))
                duration_str = duration_str.split("H")[1]
            if "M" in duration_str:
                minutes = int(duration_str.split("M")[0])
            total_hours = hours + minutes / 60

            task_data.append({
                "Task ID": task.get("id"),
                "Task Name": task.get("name"),
                "Status": task.get("status"),
                "Duration (hours)": round(total_hours, 2), 
                "Estimated Time (ms)": task.get("estimate", 0)
            })

        return pd.DataFrame(task_data)
