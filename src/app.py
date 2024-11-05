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

"""

# GitLab-tunniste ympäristömuuttujista
gitlab_token = os.getenv("GITLAB_TOKEN")

st.title("GitLab Projektin Analyysi")

# Käyttäjän syöte: GitLab-projektin linkki
project_url = st.text_input("Anna GitLab-projektin linkki:")

# Funktio projektipolun poimimiseksi linkistä (muotoa ryhma/projekti)
def extract_project_path(url):
    match = re.search(r"gitlab.dclabra.fi/(.+)", url)
    return match.group(1) if match else None

# Hae projektin ID polun perusteella
def fetch_project_id(project_path, gitlab_token):
    headers = {"Private-Token": gitlab_token}
    encoded_path = quote(project_path, safe="")  # URL-enkoodaa polku
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
                st.subheader("GitLab-tokenia löydetty ympäristömuuttujista.")
        else:
            st.error("Projektin ID:n hakeminen epäonnistui. Tarkista linkki tai projektin näkyvyysasetukset.")
    else:
        st.error("Virheellinen GitLab-linkki. Varmista, että linkki on oikeassa muodossa.")
