import requests
import os
import re
import pandas as pd

class ClockifyData:
    def __init__(self, clockify_url):
        self.clockify_url = clockify_url
        self.workspace_id = None
        self.project_id = None
        self.user_id = None
        self.api_key = os.getenv("CLOCKIFY_TOKEN")
        self.headers = {"X-Api-Key": self.api_key}

        if not self.api_key:
            raise ValueError("CLOCKIFY_TOKEN ympäristömuuttujaa ei ole asetettu!")

        self.init(clockify_url)

    def init(self, clockify_url):
        """Alustaa ClockifyData-luokan hakemalla työtilat tai muut tarvittavat tiedot."""
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
        """Hakee kaikki työtilat Clockify API:n kautta."""
        response = requests.get(f"{self.clockify_url}/workspaces", headers=self.headers)
        if response.status_code == 200:
            workspaces = response.json()
            self.workspace_id = workspaces[0]["id"] if workspaces else None
            return workspaces
        else:
            print(f"Virhe haettaessa työtiloja: {response.status_code}")
            return []

    def get_projects(self):
        """Hakee projektit tietystä työtilasta."""
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
        """Hakee käyttäjät työtilassa."""
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
                    
                    # Lisää tiedot riviin
                    data.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_seconds": seconds,
                        "duration_hours": hours  
                    })

            # Muunnetaan lista DataFrameksi
            df = pd.DataFrame(data)
            return df
        else:
            print(f"Virhe haettaessa aikakirjauksia käyttäjälle {user_id}: {response.status_code}")
            return pd.DataFrame()

    def get_all_user_hours_df(self, project_id):
        """
        Hakee kaikkien käyttäjien työtunnit tietyssä projektissa ja palauttaa DataFrame-muodossa.
        """
        users_in_workspace = self.get_users_in_workspace()
        all_user_hours = []

        for user in users_in_workspace:
            user_name = user.get("name", "Nimi ei löytynyt")
            user_id = user.get("id")
            user_time_entries_df = self.get_time_entries_df(user_id, project_id)

            if not user_time_entries_df.empty:
                # käyttäjän kokonaistyötunnit
                total_time_hours = user_time_entries_df["duration_hours"].sum()
                all_user_hours.append({"Nimi": user_name, "Työtunnit": total_time_hours})

        
        return pd.DataFrame(all_user_hours)
