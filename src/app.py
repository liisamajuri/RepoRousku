import streamlit as st
import os
import requests
import re
from urllib.parse import quote

"""
Place-holder -koodi kontin suoritustiedostolle (dockerfilessä määritetty run-komento).

Lisäksi seuraavat komponentit hyödynnettäväksi / implementoitavaksi:
- Ympäristömuuttujan tunnistus / käyttö
- Projekti-ID:n eristäminen linkistä
- fetch_all_items -funktio (looppaus datan hakemiseksi useammalta sivulta)
"""

def fetch_all_items(api_url, headers):
    """
    Hakee kaikki tietueet API-kutsusta käyttäen sivutusta.
    
    Esimerkkikäyttö:
    
    headers = {"Private-Token": gitlab_token}
    api_url = f"https://gitlab.dclabra.fi/api/v4/projects/{project_id}/repository/commits"
    commits = fetch_all_items(api_url, headers)    
    
    """
    all_items = []
    page = 1
    while True:
        response = requests.get(api_url, headers=headers, params={'per_page': 100, 'page': page})
        response.raise_for_status()
        items = response.json()
        if not items:
            break
        all_items.extend(items)
        page += 1
    return all_items


# GitLab-tunniste ympäristömuuttujista
gitlab_token = os.getenv("GITLAB_TOKEN")

st.title("RepoRousku coming soon!")

# GitLab-projektin linkki
project_url = st.text_input("GitLab-projektin linkki:")

# Poimi projektipolku linkistä
def extract_project_path(url):
    match = re.search(r"gitlab.dclabra.fi/(.+)", url)
    return match.group(1) if match else None

# Hae projektin ID polun perusteella
def fetch_project_id(project_path, gitlab_token):
    headers = {"Private-Token": gitlab_token}
    encoded_path = quote(project_path, safe="")
    api_url = f"https://gitlab.dclabra.fi/api/v4/projects/{encoded_path}"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        project_data = response.json()
        return project_data["id"]
    else:
        return None

# Poimi projektipolku linkistä ja hae projektin ID
if project_url:
    project_path = extract_project_path(project_url)
    if project_path:
        project_id = fetch_project_id(project_path, gitlab_token)
        if project_id:
            st.subheader("Projektin ID:n hakeminen onnistui.")
            # Tarkista, että token on asetettu
            if not gitlab_token:
                st.error("GitLab-tokenia ei löydy ympäristömuuttujista. Tarkista asetus.")
            else:
                st.subheader("GitLab-token löydetty ympäristömuuttujista.")
        else:
            st.error("Projektin ID:n hakeminen epäonnistui. Tarkista linkki / näkyvyysasetukset.")
    else:
        st.error("Virheellinen GitLab-linkki. Varmista, että linkki on oikeassa muodossa.")
