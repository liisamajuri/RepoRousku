import requests
import os
import re
import pandas as pd
from gitlab_api import ProjectData



class ClockifyData:
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
        self.clockify_url = clockify_url
        self.get_workspaces()

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
        response = requests.get(f"{self.clockify_url}/workspaces", headers=self.headers)
        if response.status_code == 200:
            workspaces = response.json()
            self.workspace_id = workspaces[0]["id"] if workspaces else None
            return workspaces
        else:
            print(f"Virhe haettaessa työtiloja: {response.status_code}")
            return []

    def get_projects(self):
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
        if not self.workspace_id:
            print("Työtilan ID ei ole asetettu.")
            return []

        response = requests.get(f"{self.clockify_url}/workspaces/{self.workspace_id}/users", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Virhe haettaessa käyttäjiä: {response.status_code}")
            return []

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
        Yhdistää GitLabin sprintit (milestone) ja Clockifyn työtunnit.
        Palauttaa käyttäjäkohtaiset työtunnit per sprintti valmiiksi ryhmiteltynä.
        """
        gitlab_project = ProjectData(gitlab_url, gitlab_token)
        milestones = gitlab_project.get_milestones()

        if milestones.empty:
            return pd.DataFrame()  # Palautetaan tyhjä DataFrame, jos milestoneja ei ole

        sprint_hours = []
        users_in_workspace = self.get_users_in_workspace()

        for _, milestone in milestones.iterrows():
            milestone_name = milestone['title']
            start_date = pd.Timestamp(milestone['start_date'])  # Muutetaan Timestamp-muotoon
            end_date = pd.Timestamp(milestone['due_date'])  # Muutetaan Timestamp-muotoon

            # Käydään läpi kaikki käyttäjät ja lasketaan heidän työtunnit sprintissä
            for user in users_in_workspace:
                user_id = user["id"]
                time_entries_df = self.get_time_entries_df(user_id, self.project_id)

                if not time_entries_df.empty:
                    # Muutetaan aikaleimat Timestamp-muotoon vertailua varten
                    time_entries_df['start_time'] = pd.to_datetime(time_entries_df['start_time'], format="%Y-%m-%dT%H:%M:%SZ")

                    # Suodatetaan merkinnät sprintin päivämäärien perusteella
                    sprint_entries = time_entries_df[
                        (time_entries_df['start_time'] >= start_date) & 
                        (time_entries_df['start_time'] <= end_date)
                    ]

                    # Lasketaan kokonaiskesto tunneissa
                    total_hours = sprint_entries['duration_hours'].sum()

                    # Lisätään tiedot listaan
                    sprint_hours.append({
                        "user": user["name"],
                        "milestone": milestone_name,
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_hours": total_hours
                    })

        # Luodaan DataFrame
        sprint_hours_df = pd.DataFrame(sprint_hours)

        if not sprint_hours_df.empty:
            # Ryhmitellään tiedot käyttäjän ja sprintin mukaan
            sprint_hours_df_grouped = sprint_hours_df.groupby(['user', 'milestone']).agg({'total_hours': 'sum'}).reset_index()
            return sprint_hours_df_grouped

        return pd.DataFrame()  # Palautetaan tyhjä DataFrame, jos tietoja ei ole

    def get_tags(self):
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
            pd.DataFrame: DataFrame, joka sisältää tagin nimen ja siihen liittyvät tunnit kaikille käyttäjille.
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
                continue  # Siirrytään seuraavaan käyttäjään

            # Hae aikakirjaukset tietyltä käyttäjältä ja projektilta
            url = f"{self.clockify_url}/workspaces/{self.workspace_id}/user/{user_id}/time-entries?project={project_id}"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 404:
                print(f"Projektia ei löydy ID:llä {project_id} käyttäjältä {user_id}.")
                continue  # Siirrytään seuraavaan käyttäjään
            elif response.status_code != 200:
                print(f"Virhe haettaessa aikakirjauksia projektista {project_id} käyttäjältä {user_id}: {response.status_code}")
                continue

            time_entries = response.json()

            
            for tag in tags:
                tag_id = tag["id"]
                tag_name = tag["name"]

                # Suodata aikakirjaukset, joissa on tämä tagi
                tagged_entries = [
                    entry for entry in time_entries
                    if "tagIds" in entry and tag_id in entry["tagIds"]
                ]

                
                total_hours = sum(
                    self.iso_duration_to_seconds(entry["timeInterval"].get("duration", "PT0S")) / 3600
                    for entry in tagged_entries
                )

               
                tag_hours_list.append({"user_id": user_id, "user_name": user["name"], "tag": tag_name, "total_hours": total_hours})

        
        return pd.DataFrame(tag_hours_list)







    def get_tag_hours(self):
        """Hakee ja laskee työtunnit kullekin tagille työtilassa."""
        tag_hours_list = []  # Listaa tagien kokonaistunnit

        tags = self.get_tags()
        if not tags:
            print("Ei löytynyt tageja.")
            return pd.DataFrame()

        for tag in tags:
            tag_id = tag["id"]
            tag_name = tag["name"]
            print(f"Käsitellään tagi: {tag_name}, ID: {tag_id}")

            # Haetaan aikakirjaukset tälle tagille
            time_entries_df = self.get_time_entries_by_tag(tag_ids=[tag_id])

            if not time_entries_df.empty:
                total_tag_hours = time_entries_df['duration_hours'].sum()  # Summataan tunnit
                print(f"Tagille {tag_name} kokonaistunnit: {total_tag_hours}")
                tag_hours_list.append({
                    "tag": tag_name,
                    "total_hours": total_tag_hours  # Kokonaistunnit tagille
                })
            else:
                print(f"Ei aikakirjauksia tagille {tag_name}")

        # Palautetaan DataFrame kokonaistunneista
        if tag_hours_list:
            tag_hours_df = pd.DataFrame(tag_hours_list)
            print(f"Tag Hours List: {tag_hours_df}")
            return tag_hours_df
        else:
            return pd.DataFrame()
