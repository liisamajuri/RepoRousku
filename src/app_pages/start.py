import streamlit as st
import os
import requests

import libraries.components as cl
from gitlab_api import ProjectData

# Kielikäännökset
app_title = "RepoRousku"
repo_address = "GitLab-repositorion osoite"
text_gitlab_token = "GitLab Access Token"
text_clockify_token = "Clockify Access Token"
save = "Tallenna"
crunch = "Rouskuta"
save_help = "Tallenna access tokenit. Aiemmin tallennetut access tokenit poistetaan."
help_required = "Pakollinen. Projektitietojen haku GitLabista edellyttää GitLabin access tokenia."
help_optional = "Valinnainen. Jos Clockifyn access tokenia ei määritetä, tietoja ei haeta Clockifystä."
help_repo_address = "Anna projektin päätason url"
help_crunch = "Hae projektin tiedot GitLabista"
fetching_data = "Haetaan tietoja..."
missing_g_token = "GitLab Access Token puuttuu!"
missing_url = "GitLab-projektin osoite puuttuu!"
invalid_url = "Virheellinen GitLab-projektin osoite!"
error_msg = "Tarkista GitLab-osoite ja Access Token!"

# Muuttujat
app_logo = "✨"
proj_data = "proj_data"


def get_project_data(gitlab_url, gitlab_token):
    """
    Haetaan data annetusta projektista
    """
    if gitlab_url.endswith('/'):
        gitlab_url = gitlab_url[:-1]

    gitlab_proj = ProjectData(gitlab_url, gitlab_token)
    if gitlab_proj and gitlab_proj.get_id():
        st.session_state[proj_data] = gitlab_proj
        return True
    else:
        st.session_state[proj_data] = None
        return False


def start_page():
    """
    Sivu sisältää syöttökentät GitLabin ja Clockifyn access tokenien sekä analysoitavan GitLab-projektin url-osoitteen määrittämiseen
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown(f'<h1 style="text-align: right;">{app_logo}</h1>', unsafe_allow_html=True)

    with col2:
        st.title(app_title)
        st.write("")

        env_gitlab_token = os.getenv("GITLAB_TOKEN")
        env_clockify_token = os.getenv("CLOCKIFY_TOKEN")

        gitlab_token = st.text_input(text_gitlab_token, value = env_gitlab_token, type = "password", help = help_required)
        clockify_token = st.text_input(text_clockify_token, value = env_clockify_token, type = "password", help = help_optional)
        if st.button(save, help = save_help):
            st.error("Toimintoa ei vielä toteutettu", icon="❗")

        st.write("")
        st.write("")

        gitlab_url = st.text_input(repo_address, help = help_repo_address)
        if st.button(crunch, help = help_crunch):
            if not gitlab_url:
                st.error(missing_url, icon="❗")
            elif not gitlab_token:
                st.error(missing_g_token, icon="❗")
            elif not cl.validate_url(gitlab_url):
                st.error(invalid_url, icon="❗")
            else:                
                with st.spinner(fetching_data):
                    if get_project_data(gitlab_url, gitlab_token):
                        st.switch_page('app_pages/project.py')
                    else:
                        st.error(error_msg, icon="❗")

start_page()