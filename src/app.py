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

            # Tarkista, että token on asetettu
            if not gitlab_token:
                st.error("GitLab-tokenia ei löydy ympäristömuuttujista. Tarkista asetus.")
            else:
                # Hae ja näytä projektin perustiedot
                project_info = get_project_info(project_id, gitlab_token)

                if project_info:
                    st.subheader("Projektin perustiedot")
                    st.write(f"**Nimi**: {project_info['name']}")
                    st.write(f"**ID**: {project_info['id']}")

                    # Avatar (jos saatavilla)
                    if project_info.get("avatar_url"):
                        st.image(project_info["avatar_url"], width=100)

                    # Kuvaus
                    if project_info.get("description"):
                        st.write(f"**Kuvaus**: {project_info['description']}")

                    # Luontipäivä ja viimeisin päivityspäivä
                    st.write(f"**Luontipäivä**: {project_info['created_at']}")
                    st.write(f"**Viimeisin päivitys**: {project_info['last_activity_at']}")

                    # Projektin omistaja
                    if project_info.get("owner"):
                        st.write(f"**Omistaja**: {project_info['owner']['name']}")
                        
                    # Hae ja näytä projektin statistiikkatiedot
                    st.subheader("Projektin statistiikkatiedot")
                    
                    # Commit-statistiikat
                    commit_stats = get_commit_statistics(project_id, gitlab_token)
                    st.write("**Commit Statistics:**", commit_stats)

                    # Issue-statistiikat
                    issue_stats = get_issue_statistics(project_id, gitlab_token)
                    st.write("**Issue Statistics:**", issue_stats)

                    # Branch-statistiikat
                    branch_stats = get_branch_statistics(project_id, gitlab_token)
                    st.write("**Branch Statistics:**", branch_stats)

                    # Merge request -statistiikat
                    merge_request_stats = get_merge_request_statistics(project_id, gitlab_token)
                    st.write("**Merge Request Statistics:**", merge_request_stats)

                    # Milestone-statistiikat
                    milestone_stats = get_milestone_statistics(project_id, gitlab_token)
                    st.write("**Milestone Statistics:**", milestone_stats)                            
                                              
                else:
                    st.error("Projektin perustietojen hakeminen epäonnistui.")
        else:
            st.error("Projektin ID:n hakeminen epäonnistui. Tarkista linkki tai projektin näkyvyysasetukset.")
    else:
        st.error("Virheellinen GitLab-linkki. Varmista, että linkki on oikeassa muodossa.")
