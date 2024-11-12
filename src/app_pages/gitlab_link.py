"""
Sovelluksessa piilossa oleva sivu, joka avulla generoidaan projektin 
GitLab-repositorion avaava valikkotoiminto. Toiminto ei ole käytössä 
Docker-kontin sisällä ajettavassa sovellusversiossa.
"""
import streamlit as st
import webbrowser
import libraries.components as cl

# Kielikäännökset
gitlab_title = "GitLab"

# Muuttujat
proj_data = "proj_data"


def gitlab_link_page():
    """
    Avaa projetin GitLab-repositorion sivun
    """
    if cl.in_docker():
        st.write(st.session_state[proj_data].get_project_url())
    else:
        webbrowser.open(st.session_state[proj_data].get_project_url())
        st.switch_page("app_pages/project.py")


cl.make_page_title(gitlab_title)

if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    gitlab_link_page()

