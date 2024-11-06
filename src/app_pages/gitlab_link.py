import streamlit as st
import webbrowser
import libraries.components as cl

# Kielikäännökset
gitlab_title = "GitLab"

# Muuttujat
proj_data = "proj_data"


def gitlab_link_page():
    """
    Sivu, joka avaa projetin GitLab-repositorion sivun
    """
    if not True: #st.session_state[proj_data]:
        cl.make_page_title(gitlab_title)
        cl.make_start_page_button() 
    else:
        webbrowser.open("https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut")
        st.switch_page('app_pages/project.py')    

gitlab_link_page()
