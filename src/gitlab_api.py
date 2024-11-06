import requests
import json
import re
import pandas as pd

from datetime import datetime
from urllib.parse import quote

import libraries.components as cl

key_id = "id"
key_name = "name"
key_desc = "description"
key_created_at = "created_at"
key_namespace = "namespace"
key_visibility = "visibility"
key_updated = "last_activity_at"

key_milestones = "milestones"
key_issues = "issues"
key_commits = "commits"
key_branches = "branches"
key_merge_requests = "merge_requests"
key_labels = "labels"
key_pipelines = "pipelines"

key_expired = "expired"
key_state = "state"
key_assignees = "assignees"

value_opened = "opened"
value_closed = "closed"
value_opened = "opened"

project_data = [key_milestones, key_issues, key_commits, key_branches, key_labels, key_merge_requests, key_pipelines]


class ProjectData:
    def __init__(self, gitlab_url, gitlab_token):
        """
        Konstruktori
        """
        self.project_url = None         # Esim. https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut
        self.api_url = None             # Esim. https://gitlab.dclabra.fi/api/v4/projects  
        self.project_data = None        # project_data -muuttujassa määritellyt tiedot api-rajapinnasta
        self.project_meta_data = None   # projektin yleistiedot

        self.access_token = gitlab_token
        self.headers = {"PRIVATE-TOKEN": self.access_token}
        self.output_file_name = 'gitlab_data.json'
        self.output_file_name2 = 'gitlab_meta_data.json'

        self.init(gitlab_url)


    ### Getterit

    def get_meta_data(self, data_type):
        return self.project_meta_data[data_type] if self.project_meta_data else None


    def get_data(self, data_type):
        return self.project_data[data_type] if self.project_data else None


    def get_name(self):
        return self.get_meta_data(key_name)


    def get_id(self):
        return self.get_meta_data(key_id)


    def get_description(self):
        return self.get_meta_data(key_desc)


    def get_project_url(self):
        return self.project_url


    def get_creation_date(self):
        """
        Palauttaa projektin luontipäivämäärän formaatissa pp.kk.vvvv
        """
        return self.format_date(self.get_meta_data(key_created_at))


    def get_update_date(self):
        """
        Palauttaa projektin viimeisimmän päivityspäivämäärän formaatissa pp.kk.vvvv
        """
        return self.format_date(self.get_meta_data(key_updated))


    def get_namespace_name(self):
        namespace = self.get_meta_data(key_namespace)
        if namespace:
            return namespace[key_name]
        return None


    def get_visibility(self):
        return self.get_meta_data(key_visibility)


    def get_milestones(self):
        """
        Palauttaa milestonetiedot dataframena
        """
        milestones = self.get_data(key_milestones)
        df = pd.DataFrame(milestones)

        df['start_date'] = pd.to_datetime(df['start_date']).dt.date
        df['due_date'] = pd.to_datetime(df['due_date']).dt.date

        # Järjestetään aikajärjestykseen
        df = df.sort_values(by='start_date')

        # Lisätään status "Päättynyt", "Aktiivinen", tai "Tuleva"
        today = datetime.now().date()

        def milestone_status(row):
            if row['due_date'] < today:
                return "Päättynyt"
            elif row['start_date'] <= today <= row['due_date']:
                return "Aktiivinen"
            else:
                return "Tuleva"

        df['status'] = df.apply(milestone_status, axis=1)

        return df


    def get_issues(self):
        """
        Palauttaa issuetiedot dataframena
        """
        issues = self.get_data(key_issues)

        # Muutetaan json dataframeksi
        df = pd.DataFrame(issues)

        # Pelkistetään assignees listaksi nimistä
        df['assignees'] = df['assignees'].apply(lambda x: x[0]['name'] if x else None)

        # Pelkistetään milestone titleksi
        df['milestone'] = df['milestone'].apply(lambda x: x['title'] if isinstance(x, dict) and 'title' in x else None)

        # Valitaan sarakkeet
        df = df[['iid', 'title', 'description', 'state', 'assignees', 'milestone']]

        return df


    def get_commits(self):
        """
        Palauttaa committien tiedot dataframena
        """
        commits = self.get_data(key_commits)
        df = pd.DataFrame(commits)
        return df


    def get_branches(self):
        """
        Palauttaa branchien tiedot dataframena
        """
        branches = self.get_data(key_branches)
        df = pd.DataFrame(branches)
        return df


    def count_branches(self):
        """
        Palauttaa branchien lukumäärän
        """
        return 0
        # TODO
        #branches = self.get_data(key_branches)
        #if branches is not None:
        #    return len(pd.DataFrame(branches))
        #return 0


    def get_labels(self):
        """
        Palauttaa labelien tiedot dataframena
        """
        labels = self.get_data(key_labels)
        df = pd.DataFrame(labels)
        return df


    def get_merge_requests(self):
        """
        Palauttaa merge requestien tiedot dataframena
        """
        merge_requests = self.get_data(key_merge_requests)
        df = pd.DataFrame(merge_requests)
        return df


    def count_open_merge_requests(self):
        """
        Palauttaa avoimien merge requestien lukumäärän
        """
        merge_requests = self.get_data(key_merge_requests)
        if merge_requests:
            return sum(1 for mr in merge_requests if mr[key_state]==value_opened)
        else:
            return 0


    def get_pipelines(self):
        """
        Palauttaa pipe linejen tiedot dataframena
        """
        pipelines = self.get_data(key_pipelines)
        df = pd.DataFrame(pipelines)
        return df


    def get_expired_milestones(self):
        """
        Palauttaa päättyneiden milestonejen lukumäärän
        """
        milestones = self.get_data(key_milestones)
        return sum(1 for milestone in milestones if milestone[key_expired])


    def get_active_milestones(self):
        """
        Palauttaa aktiivisten milestonejen lukumäärän
        """
        milestones = self.get_data(key_milestones)
        today = datetime.now().date()
        active_milestones = [milestone for milestone in milestones if (datetime.fromisoformat(milestone['start_date']).date() <= today and datetime.fromisoformat(milestone['due_date']).date() >= today)]
        return len(active_milestones)


    def get_upcoming_milestones(self):
        """
        Palauttaa tulevien milestonejen lukumäärän
        """
        milestones = self.get_data(key_milestones)
        today = datetime.now().date()
        upcoming_milestones = [milestone for milestone in milestones if datetime.fromisoformat(milestone['start_date']).date() > today]
        return len(upcoming_milestones) if upcoming_milestones else 0


    def count_milestones(self):
        """
        Palauttaa milestonejen kokonaislukumäärän
        """
        milestones = self.get_data(key_milestones)
        return len(milestones)


    def count_issues(self):
        """
        Palauttaa issueiden kokonaislukumäärän
        """
        issues = self.get_data(key_issues)
        return len(issues)


    def get_open_issues(self):
        """
        Palauttaa avoimien issueiden lukumäärän
        """
        issues = self.get_data(key_issues)
        return sum(1 for issue in issues if issue[key_state]==value_opened)


    def get_closed_issues(self):
        """
        Palauttaa suljettujen issueiden lukumäärän
        """
        issues = self.get_data(key_issues)
        return sum(1 for issue in issues if issue[key_state]==value_closed)


    def get_assignees(self):
        """
        Palauttaa listan uniikeista henkilönimistä, jotka on kerätty projektin issueista
        """
        assignees_list = []
        issues = self.get_data(key_issues)

        for issue in issues:
            for assignee in issue[key_assignees]:
                assignees_list.append({
                    key_id: assignee[key_id],
                    key_name: assignee[key_name]
                })

        df_assignees = pd.DataFrame(assignees_list)
        df_unique_assignees = df_assignees.drop_duplicates().reset_index(drop=True)
        name_list = df_unique_assignees['name'].tolist()

        return  name_list  


    def reset(self):
        """
        Resetoi olion tiedot 
        """
        self.project_url = None
        self.api_url = None
        self.project_data = None
        self.project_meta_data = None


    def fetch_data(self, url, params={}):
        """
        Suorittaa hakupyynnön GitLabin REST APIin
        """
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return None
        else:
            return None


    def fetch_data_NOT_WORKING(self, url, params={}):
        """
        Suorittaa hakupyynnön GitLabin REST APIin
        """
        all_items = []
        page = 1

        while True:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                items = response.json()
            except requests.exceptions.HTTPError:
                return None
            if not items:
                break
            all_items.extend(items)
            page += 1

        return all_items


    def fetch_api_data(self, data_type):
        """
        Suorittaa hakupyynnön GitLabin REST APIin
        """
        url = f"{self.api_url}/{self.get_id()}/{data_type}"
        #params = {'per_page': 100, 'page': page}
        return self.fetch_data(url)


    def generate_api_url(self, project_url):
        """
        Muodostaa GitLab-projektin url-osoitteesta kyseisen GitLab-instanssin REST API -osoitteen
        """
        # Erotetaan isäntänimi esim. "https://gitlab.com" tai "https://your-gitlab-instance.com"
        pattern = r'^(https://[^/]+)/(.*)$'
        match = re.match(pattern, project_url)
        if match:
            host = match.group(1)
            return f"{host}/api/v4/projects"
        return None
        

    def format_date(self, orig_date):
        """
        Palauttaa päivämäärän muodossa pp.kk.vvvv
        """
        return datetime.strptime(orig_date[:10], "%Y-%m-%d").strftime("%d.%m.%Y")


    def get_project_data(self):
        """
        Hakee projektin tiedot oliolle
        """
        all_data = {}

        for part in project_data:
            all_data[part] = self.fetch_api_data(part)

        return all_data


    def get_project_meta_data(self):
        """
        Hakee projektin yleistiedot oliolle
        """
        project_data = None

        match = re.search(r"^https://[^/]+/(.*)", self.project_url)
        project_path = match.group(1) if match else None
        if project_path:
            encoded_path = quote(project_path, safe="")
            url = f"{self.api_url}/{encoded_path}"
            project_data = self.fetch_data(url)

        return project_data


    def init(self, url):
        """
        Hakee projektin tiedot GitLabista ja asettaa ne oliolle
        """
        if cl.validate_url(url):
            api_url = self.generate_api_url(url)
            if api_url:
                data_json = self.fetch_data(api_url)
                if data_json:
                    self.project_url = url
                    self.api_url = api_url
                    self.project_meta_data = self.get_project_meta_data()
                    self.project_data = self.get_project_data()

                    if not self.project_meta_data or not self.project_data:
                        self.reset()


    def save_data_to_file(self):
        """
        Tallentaa projektin tiedot tiedostoon json-formaatissa
        """
        with open(self.output_file_name, 'w') as f:
            json.dump(self.project_data, f, indent=4)
        with open(self.output_file_name2, 'w') as f:
            json.dump(self.project_meta_data, f, indent=4)

