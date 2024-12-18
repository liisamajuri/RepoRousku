"""
RepoRouskun rajapinta, joka hakee projektin tiedot GitLabin APIsta.
Sisältää ProjectData-luokan, joka kapseloi projektin tiedot ja tarjoaa 
palveluinaan pureskeltua dataa käyttöliittymää varten.

Pääsääntönä on, että RepoRouskun tiedostoista vain tässä tiedostossa
esiintyy GitLabista saadun json-muotoisen datan avaimia.
"""

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
key_closed_at = "closed_at"
key_namespace = "namespace"
key_visibility = "visibility"
key_updated = "last_activity_at"
key_milestone = "milestone"
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
key_start_date = "start_date"
key_due_date = "due_date"
key_iid = "iid"
key_title = "title"
key_author_name = "author_name"
key_committed_date = "committed_date"
key_status = "status"
key_message = "message"
key_avatar = "avatar_url"

key_pcs = "kpl"
key_member = "jäsen"
key_date = "pvm"

value_opened = "opened"
value_closed = "closed"
value_active = "active"

status_upcoming = "Tuleva"
status_active = "Aktiivinen"
status_ended = "Päättynyt"

project_data = [key_milestones, key_issues, key_commits, key_branches, key_labels, key_merge_requests, key_pipelines]


class ProjectData:
    """
    Luokka GitLab-projektin tietojen hakemiseen ja käsittelyyn.
    """
    def __init__(self, gitlab_url, gitlab_token):
        """
        Konstruktori
        """
        self.project_url = None         # Esim. https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut
        self.api_url = None             # Esim. https://gitlab.dclabra.fi/api/v4/projects  
        self.project_data = None        # project_data -muuttujassa määritellyt tiedot api-rajapinnasta
        self.project_meta_data = None   # projektin yleistiedot

        self.access_token = gitlab_token
        self.headers = {"Private-Token": self.access_token}
        self.output_file_name = 'gitlab_data.json'
        self.output_file_name2 = 'gitlab_meta_data.json'

        self.init(gitlab_url)


    ### Projektin metatietojen getterit

    def get_meta_data(self, data_type):
        """
        Palauttaa parametrina määritellyn arvon projektin metadatasta.

        Args:
            data_type (str): Pyydetyn tietokentän nimi.
        """
        return self.project_meta_data[data_type] if self.project_meta_data else None


    def get_name(self):
        """
        Palauttaa projektin nimen.

        Returns:
            (str): Projektin nimi.
        """
        return self.get_meta_data(key_name)


    def get_id(self):
        """
        Palauttaa projektin id:n.

        Returns:
            (str): Projektin id
        """
        return self.get_meta_data(key_id)


    def get_description(self):
        """
        Palauttaa projektin kuvauksen.

        Returns:
            (str): Projektin kuvaus.
        """
        return self.get_meta_data(key_desc)


    def get_visibility(self):
        """
        Palauttaa projektin näkyvyyden.

        Returns:
            (str): Projektin näkyvyys.
        """
        return self.get_meta_data(key_visibility)


    def get_avatar(self):
        """
        Palauttaa projektin avattaren urlin.

        Returns:
            (str): Projektin avattaren url.
        """
        url = self.get_meta_data(key_avatar)
        return url if url else None


    ### Projektin tietojen getterit

    def get_data(self, data_type):
        """
        Palauttaa parametrina määritellyn arvon projektin datasta.

        Args:
            data_type (str): Pyydetyn tietokentän nimi.
        """
        return self.project_data[data_type] if self.project_data else None


    def get_project_url(self):
        """
        Palauttaa projektin urlin.

        Returns:
            (str): Projektin url.
        """
        return self.project_url


    def get_creation_date(self):
        """
        Palauttaa projektin luontipäivämäärän formaatissa pp.kk.vvvv.

        Returns:
            (date): Projektin luontipäivämäärä.
        """
        return self.format_date(self.get_meta_data(key_created_at))


    def get_update_date(self):
        """
        Palauttaa projektin viimeisimmän päivityspäivämäärän formaatissa pp.kk.vvvv.

        Returns:
            (date): Projektin luontipäivämäärä.
        """
        return self.format_date(self.get_meta_data(key_updated))


    def get_namespace_name(self):
        """
        Palauttaa projektin nimiavaruuden nimen.

        Returns:
            (str): Projektin nimiavaruuden nimi.
        """
        namespace = self.get_meta_data(key_namespace)
        if namespace:
            return namespace[key_name]
        return None


    def get_milestones(self):
        """
        Palauttaa milestonetiedot dataframena.

        Returns:
            (DataFrame): Projektin milestonet.
        """
        milestones = self.get_data(key_milestones)
        if milestones:
            df = pd.DataFrame(milestones)

            if not df.empty:
                # Päivämääräformaatti
                df = cl.format_time_columns(df, [key_start_date, key_due_date])

                # Poistetaan rivit, joilla ei ole päivämäärätietoa
                df = df.dropna(subset=[key_due_date, key_start_date])

                if len(df):
                    # Järjestetään aikajärjestykseen
                    df = df.sort_values(by=key_start_date)

                    # Lisätään status "Päättynyt", "Aktiivinen", tai "Tuleva"
                    today = datetime.now().date()

                    def milestone_status(row):
                        if row[key_state] == value_closed or row[key_due_date] < today:
                            return status_ended
                        elif row[key_start_date] <= today <= row[key_due_date]:
                            return status_active
                        elif row[key_due_date] > today:
                            return status_upcoming
                        else:
                            return "EOS"

                    df[key_status] = df.apply(milestone_status, axis=1)

                    # Valitaan sarakkeet
                    df = df[[key_iid, key_title, key_desc, key_state, key_due_date, key_start_date, key_status]]

            return df
        return pd.DataFrame()


    def get_issues(self):
        """
        Palauttaa issuetiedot dataframena.

        Returns:
            (DataFrame): Projektin kaikki issuet.
        """
        issues = self.get_data(key_issues)
        if issues:
            df = pd.DataFrame(issues)

            if not df.empty:
                # Päivämääräformaatti
                df = cl.format_time_columns(df, [key_closed_at])

                # Pelkistetään assignees listaksi nimistä, jos se ei ole tyhjä
                df[key_assignees] = df[key_assignees].apply(lambda x: [assignee[key_name] for assignee in x] if isinstance(x, list) and x else None)

                # Pelkistetään milestone titleksi, jos milestone on sanakirja ja siinä on title-avain
                df[key_milestone] = df[key_milestone].apply(lambda x: x.get(key_title) if isinstance(x, dict) and key_title in x else None)

                # Valitaan sarakkeet
                df = df[[key_iid, key_title, key_desc, key_state, key_assignees, key_milestone, key_closed_at]]

            return df
        return pd.DataFrame()


    def get_commits(self, members=None):
        """
        Palauttaa committien tiedot dataframena.
        Suodatetaan jäsenten mukaan, jos jäsenet määritelty parametrissa.

        Args:
            members (list, optional): Lista jäsenten nimistä, joiden mukaan tiedot suodatetaan.

        Returns:
            (DataFrame): Jäsenten commitit.
        """
        commits = self.get_data(key_commits)
        if commits:
            df = pd.DataFrame(commits)

            if not df.empty:
                # Suodatetaan jäsenten mukaan
                if members:
                    df = df[df[key_author_name].isin(members)]

                # Päivämääräformaatti
                df = cl.format_time_columns(df, [key_committed_date])

                # Valitaan sarakkeet
                df = df[[key_title, key_message, key_author_name, key_committed_date]]

            return df
        return pd.DataFrame()


    def get_branches(self):
        """
        Palauttaa branchien tiedot dataframena.

        Returns:
            (DataFrame): Projektin branchit.
        """
        branches = self.get_data(key_branches)
        if branches:
            df = pd.DataFrame(branches)
            return df
        return pd.DataFrame()


    def count_branches(self):
        """
        Palauttaa branchien lukumäärän.

        Returns:
            (int): Projektin branchien lukumäärä.
        """
        branches = self.get_branches()
        return len(branches)


    def get_labels(self):
        """
        Palauttaa labelien tiedot dataframena.

        Returns:
            (DataFrame): Projektin labelit.
        """
        labels = self.get_data(key_labels)
        if labels:
            df = pd.DataFrame(labels)
            return df
        return pd.DataFrame()


    def get_merge_requests(self):
        """
        Palauttaa merge requestien tiedot dataframena.

        Returns:
            (DataFrame): Projektin avoimet merge requestit.
        """
        merge_requests = self.get_data(key_merge_requests)
        if merge_requests:
            df = pd.DataFrame(merge_requests)
            return df
        return pd.DataFrame()


    def count_open_merge_requests(self):
        """
        Palauttaa avoimien merge requestien lukumäärän.

        Returns:
            (int): Projektin avoimien merge requestien lukumäärä.
        """
        df = self.get_merge_requests()
        if len(df):
            return len(df[df[key_state] == value_opened])
        else:
            return 0


    def get_pipelines(self):
        """
        Palauttaa pipelinejen tiedot dataframena.

        Returns:
            (DataFrame): Projektin pipelinet.
        """
        pipelines = self.get_data(key_pipelines)
        if pipelines:
            df = pd.DataFrame(pipelines)
            return df
        return pd.DataFrame()


    def count_expired_milestones(self):
        """
        Palauttaa päättyneiden milestonejen lukumäärän.

        Returns:
            (int): Projektin päättyneiden milestonejen lukumäärä.
        """
        df = self.get_milestones()
        if len(df):
            return len(df[df[key_state] == value_closed])
        return 0


    def count_active_milestones(self):
        """
        Palauttaa aktiivisten milestonejen lukumäärän.

        Returns:
            (int): Projektin aktiivisten milestonejen lukumäärä.
        """
        df = self.get_milestones()
        if len(df):
            return len(df[df[key_status] == status_active])
        return 0


    def count_upcoming_milestones(self):
        """
        Palauttaa tulevien milestonejen lukumäärän.

        Returns:
            (int): Projektin tulevien milestonejen lukumäärä.
        """
        df = self.get_milestones()
        if len(df):
            return len(df[df[key_status] == status_upcoming])
        return 0


    def get_readiness_ml(self):
        """
        Palauttaa projektin valmiusasteen milestonejen mukaan.

        Returns:
            (int): Projektin milestonetason valmiusaste kokonaislukuprosenttina.
        """
        expired = self.count_expired_milestones()
        all_milestones = self.count_milestones()
        if expired and all_milestones:
            return round((expired / all_milestones) * 100)
        return 0


    def count_milestones(self):
        """
        Palauttaa milestonejen kokonaislukumäärän.

        Returns:
            (int): Projektin milestonejen lukumäärä.
        """
        df = self.get_milestones()
        if len(df):
            return len(df)
        return 0


    def get_open_issues(self):
        """
        Palauttaa avoimet issuet.

        Returns:
            (DataFrame): Projektin avoimet issuet.
        """
        df = self.get_issues()
        if not df.empty:
            df = df[df[key_state] == value_opened]
            return df
        return pd.DataFrame()


    def count_open_issues(self):
        """
        Palauttaa avoimien issueiden lukumäärän.

        Returns:
            (int): Projektin avoimien issueiden lukumäärä.
        """
        df = self.get_open_issues()
        return len(df)


    def get_closed_issues(self):
        """
        Palauttaa suljetut issuet.

        Returns:
            (DataFrame): Projektin suljetut issuet.
        """
        df = self.get_issues()
        if not df.empty:
            df = df[df[key_state] == value_closed]
            return df
        return pd.DataFrame()


    def get_readiness_issues(self):
        """
        Palauttaa projektin valmiusasteen issueiden mukaan.

        Returns:
            (int): Projektin issuetason valmiusaste kokonaislukuprosenttina.
        """
        all_issues = len(self.get_issues())
        closed = len(self.get_closed_issues())
        if all_issues and closed:
            return round((closed / all_issues) * 100)
        return 0


    def get_assignees(self):
        """
        Palauttaa listan uniikeista henkilönimistä, jotka on kerätty projektin issueista ja commiteista.

        Returns:
            (list): Lista uniikeista henkilönimistä.
        """
        issue_members = []
        commit_members = []
        issues = self.get_issues()
        commits = self.get_commits()

        if not issues.empty:
            issue_members = issues.explode(key_assignees)[key_assignees].dropna().unique().tolist()

        if not commits.empty:
            commit_members = commits[key_author_name].dropna().unique().tolist()

        return sorted(set(issue_members + commit_members))


    def reset(self):
        """
        Resetoi olion tiedot.
        """
        self.project_url = None
        self.api_url = None
        self.project_data = None
        self.project_meta_data = None


    def fetch_data(self, url, params={}):
        """
        Suorittaa hakupyynnön GitLabin REST APIin.

        Args:
            url (str): Projektin GitLab-url.
            params (dict): GET-kutsun parametrilista.

        Returns:
            (json): Haetut tiedot tai None.
        """
        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code == 200:
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return None
        else:
            return None


    def fetch_data_with_pagination(self, url, params={}):
        """
        Suorittaa hakupyynnön GitLabin REST APIin.

        Args:
            url (str): Projektin GitLab-url.
            params (dict): GET-kutsun parametrilista.

        Returns:
            (json): Haetut tiedot tai None.
        """
        all_items = []
        page = 1

        while True:
            try:
                params = {**params, 'per_page': 100, 'page': page}
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                items = response.json()
                if not items:
                    break
            except requests.exceptions.HTTPError:
                return None
            all_items.extend(items)
            page += 1

        return all_items


    def generate_api_url(self, project_url):
        """
        Muodostaa GitLab-projektin url-osoitteesta kyseisen GitLab-instanssin REST API -osoitteen.

        Args:
            project_url (str): Projektin GitLab-url.

        Returns:
            (str): GitLabin REST API -osoite.
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
        Palauttaa päivämäärän muodossa pp.kk.vvvv.

        Args:
            orig_date (datetime): Päivämäärä.

        Returns:
            (str): Päivämäärän muodossa pp.kk.vvvv.
        """
        return datetime.strptime(orig_date[:10], "%Y-%m-%d").strftime("%d.%m.%Y")


    def get_project_data(self):
        """
        Hakee projektin tiedot oliolle.

        Returns:
            (json): Projektin tiedot.
        """
        all_data = {}

        for data_type in project_data:
            if data_type == key_commits or data_type == key_branches:
                url = f"{self.api_url}/{self.get_id()}/repository/{data_type}"
            else:
                url = f"{self.api_url}/{self.get_id()}/{data_type}"
            all_data[data_type] = self.fetch_data_with_pagination(url)

        return all_data


    def get_project_meta_data(self):
        """
        Hakee projektin yleistiedot oliolle.

        Returns:
            (json): Projektin metatiedot.
        """
        if not self.project_url:
            return None    
        
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
        Hakee projektin tiedot GitLabista ja asettaa ne oliolle.

        Args:
            url (str): Projektin GitLab-url.
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
        Tallentaa projektin tiedot tiedostoon json-formaatissa.
        """
        with open(self.output_file_name, 'w') as f:
            json.dump(self.project_data, f, indent=4)
        with open(self.output_file_name2, 'w') as f:
            json.dump(self.project_meta_data, f, indent=4)


    def get_date_limits_for_closed_issues(self, members):
        """
        Palauttaa aikajakson, jolloin parametrin members jäsenien issueita on suljettu.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan issuet suodatetaan.

        Returns:
            (tuple): Aikajakson ensimmäinen ja viimeinen päivämäärä.
        """
        df = self.get_closed_issues()

        # Assigneet omille riveilleen
        df = df.explode(key_assignees)

        # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
        df = df[df[key_assignees].isin(members)]

        if len(df):
            # Päivämäärärajat liukusäädintä varten
            min_date = df[key_closed_at].min()
            max_date = df[key_closed_at].max()
            return min_date, max_date
        else:
            return 0,0


    def get_date_limits_for_commits(self, members):
        """
        Palauttaa aikajakson, jolloin parametrin members jäsenet ovat tehneet committeja.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan commitit suodatetaan.

        Returns:
            (tuple): Aikajakson ensimmäinen ja viimeinen päivämäärä.
        """
        df = self.get_commits(members)

        if len(df):
            # Päivämäärärajat liukusäädintä varten
            min_date = df[key_committed_date].min()
            max_date = df[key_committed_date].max()
            return min_date, max_date
        else:
            return 0,0


    def get_closed_issues_by_date(self, members, min_date=None, max_date=None):
        """
        Palauttaa dataframen suljetuista issueista päivämäärän mukaan.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan issuet suodatetaan.
            min_date (date): Aikajakson ensimmäinen päivämäärä.
            max_date (date): Aikajakson viimeinen päivämäärä.

        Returns:
            (DataFrame): Suljetut issuet jäsenten ja aikajakson mukaan suodatettuna.
            (str): Päivämääräakselin nimi.
            (str): Kappalemääräakselin nimi.
        """
        df = self.get_closed_issues()

        # Assigneet omille riveilleen
        df = df.explode(key_assignees)

        # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
        df = df[df[key_assignees].isin(members)]

        df[key_closed_at] = df[key_closed_at]

        # Datasta löytyvät ajanjakson alku- ja loppupäivät
        start_date = df[key_closed_at].min() if len(df) else None
        end_date = df[key_closed_at].max() if len(df) else None

        # Suodatetaan ajanjakson mukaan, jos se on määritelty
        if min_date and max_date:
            start_date = pd.to_datetime(min_date).date()
            end_date = pd.to_datetime(max_date).date()
            df = df[(df[key_closed_at] >= start_date) & (df[key_closed_at] <= end_date)]

        # Ryhmitellään data päivämäärän ja jäsenen mukaan
        df = df.groupby([df[key_closed_at], key_assignees]).size().unstack(fill_value=0)

        if start_date and end_date and start_date != end_date:
            # Täydennetään dataframe, että kaikki päivämäärät ajanjaksolta ovat mukana
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # Varmistetaan, että indeksi on päivämäärä
            df.index = pd.to_datetime(df.index)

            # Täydennetään dataframe issuettomilla päivämäärillä (puuttuvat päivämäärät saavat arvon 0)
            df = df.reindex(date_range, fill_value=0)
        else:
            df.index = pd.to_datetime(df.index)

        # Asetetaan päivämäärä indekseiksi ja jäsenet sarakkeiksi
        df.index = df.index.strftime('%Y-%m-%d')

        return df, key_date, key_pcs


    def get_commits_by_date(self, members, min_date=None, max_date=None):
        """
        Palauttaa dataframen commiteista päivämäärän mukaan.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan issuet suodatetaan.
            min_date (date): Aikajakson ensimmäinen päivämäärä.
            max_date (date): Aikajakson viimeinen päivämäärä.

        Returns:
            (DataFrame): Commitit jäsenten ja aikajakson mukaan suodatettuna.
            (str): Päivämääräakselin nimi.
            (str): Kappalemääräakselin nimi.
        """
        df = self.get_commits(members)

        start_date = df[key_committed_date].min() if len(df) else None
        end_date = df[key_committed_date].max() if len(df) else None

        # Suodatetaan ajanjakson mukaan, jos se on määritelty
        if min_date and max_date:
            start_date = pd.to_datetime(min_date).date()
            end_date = pd.to_datetime(max_date).date()
            df = df[(df[key_committed_date] >= start_date) & (df[key_committed_date] <= end_date)]

        # Uudelleennimetään sarakkeita kaaviota varten
        df = df.rename(columns={key_author_name: key_member, key_committed_date: key_date})

        # Ryhmitellään data päivämäärän ja jäsenen mukaan
        df = df.groupby([df[key_date], key_member]).size().unstack(fill_value=0)


        if start_date and end_date:
            # Täydennetään dataframe, että kaikki päivämäärät ajanjaksolta ovat mukana
            date_range = pd.date_range(start=start_date, end=end_date, freq='D')

            # Varmistetaan, että indeksi on päivämäärä
            df.index = pd.to_datetime(df.index)

            # Täydennetään dataframe issuettomilla päivämäärillä (puuttuvat päivämäärät saavat arvon 0)
            df = df.reindex(date_range, fill_value=0)
        else:
            df.index = pd.to_datetime(df.index)

        # Asetetaan päivämäärä indekseiksi ja jäsenet sarakkeiksi
        df.index = df.index.strftime('%Y-%m-%d')

        return df, key_date, key_pcs


    def get_closed_issues_by_milestone(self, members):
        """
        Palauttaa dataframen suljetuista issueista milestonejen mukaan.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan issuet suodatetaan.

        Returns:
            (DataFrame): Suljetut issuet jäsenten mukaan suodatettuna.
            (str): Päivämääräsarakkeen nimi.
            (str): Kappalemääräsarakkeen nimi.
            (str): Jäsensarakkeen nimi.
        """
        df = self.get_closed_issues()

        # Assigneet omille riveilleen
        df_exploded = df.explode(key_assignees)

        # Suodatetaan jäsenet
        df_filtered = df_exploded[df_exploded[key_assignees].isin(members)]

        # Lasketaan issueiden määrä kullekin milestone ja assignees -yhdistelmälle
        grouped_data = df_filtered.groupby([key_milestone, key_assignees]).size().reset_index(name=key_pcs)

        # Lisätään puuttuvat milestone-assignee-yhdistelmät
        df_milestones = self.get_milestones()

        if len(df_milestones):
            all_milestones = df_milestones[key_title].unique()
            grouped_data = (
                grouped_data.set_index([key_milestone, key_assignees])
                .reindex(pd.MultiIndex.from_product([all_milestones, members], names=[key_milestone, key_assignees]), fill_value=0)
                .reset_index())

            # Uudelleennimetään sarake
            grouped_data = grouped_data.rename(columns={key_assignees: key_member})

            # Lukumäärä kokonaisluvuksi
            grouped_data[key_pcs] = grouped_data[key_pcs].astype(int)

            return grouped_data, key_milestone, key_pcs, key_member

        else:
            return pd.DataFrame(), key_milestone, key_pcs, key_member


    def get_commits_by_milestone(self, members):
        """
        Palauttaa dataframen commiteista milestonejen mukaan.

        Args:
            members (list): Lista jäsenten nimistä, joiden mukaan commitit suodatetaan.

        Returns:
            (DataFrame): Commitit jäsenten mukaan suodatettuna.
            (str): Milestonesarakkeen nimi.
            (str): Kappalemääräsarakkeen nimi.
            (str): Jäsensarakkeen nimi.
        """
        df_commits = self.get_commits(members)
        df_milestones = self.get_milestones()

        if len(df_commits) and len(df_milestones):
            # Liitetään milestone commit-päivämäärän perusteella
            def get_milestone_for_commit(commit_date):
                milestone = df_milestones[(df_milestones[key_start_date] <= commit_date) & (df_milestones[key_due_date] >= commit_date)]
                return milestone[key_title].iloc[0] if not milestone.empty else None

            # Lisätään tieto milestonesta committien dataframeen
            df_commits[key_milestone] = df_commits[key_committed_date].apply(get_milestone_for_commit)

            # Suodatetaan pois commitit, joille ei löytynyt milestonea
            df_commits = df_commits.dropna(subset=[key_milestone])

            # Lasketaan commit-määrät per milestone ja jäsen
            grouped_data = df_commits.groupby([key_milestone, key_author_name]).size().reset_index(name=key_pcs)

            # Varmistetaan, että data on oikeassa muodossa kaaviota varten
            grouped_data.columns = [key_milestone, key_member, key_pcs]

            # Lisätään puuttuvat milestone-assignee-yhdistelmät
            df_milestones = self.get_milestones()
            all_milestones = df_milestones[key_title].unique()
            grouped_data = (
                grouped_data.set_index([key_milestone, key_member])
                .reindex(pd.MultiIndex.from_product([all_milestones, members], names=[key_milestone, key_member]), fill_value=0)
                .reset_index())

            # Lukumäärät kokonaisluvuksi
            grouped_data[key_pcs] = grouped_data[key_pcs].astype(int)

            return grouped_data, key_milestone, key_pcs, key_member

        return pd.DataFrame(columns=[key_milestone, key_pcs, key_member]), key_milestone, key_pcs, key_member


    def get_milestone_data_for_slider(self, start_date_column, end_date_column):
        """
        Muodostaa milestonejen nimistä sekä aloitus- ja lopetuspäivämääristä dataframen.

        Args:
            start_date_column (str): Alkupäivämäärälle asetettava sarakenimi.
            end_date_column (str): Loppupäivämäärälle asetettava sarakenimi.

        Returns:
           (DataFrame): Milestonet alku- ja loppupäivämäärineen.
        """
        df = self.get_milestones()

        if len(df):
            # Varmistetaan, että milestonet ovat järjestyksessä
            df = df.sort_values(by=key_iid, ascending=True)

            # Valitaan milestonet, jotka ovat päättyneet tai aktiivinen
            df = df[(df[key_status] == status_ended) | (df[key_status] == status_active)]

            # Valitaan sarakkeet
            df = df[[key_title, key_start_date, key_due_date]]

            # UUdelleennimetään sarakkeita
            df = df.rename(columns={key_start_date: start_date_column, key_due_date: end_date_column})

        return df