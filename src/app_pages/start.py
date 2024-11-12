"""
RepoRouskun etusivu, jonka avulla käyttäjä määrittelee tarkasteltavan projektin ja tarvittavat pääsyoikeudet projektin dataan.
Käyttäjän tulee antaa vähintään projektin GitLab-repositorion URL ja Access Token. Jos käyttäjä määrittää lisäksi 
GitLab-projektiin liittyvän Clockify-projektin ja sen Access Tokenin, on sovelluksessa mahdollista tarkastella myös 
projektin ajankäyttöä.
"""

import streamlit as st
import os
from dotenv import load_dotenv

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
missing_token_values = "Access Token(it) puuttuu!"

gitlab_token = "GITLAB_TOKEN"
clockify_token = "CLOCKIFY_TOKEN"

# Muuttujat
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
        #st.session_state[proj_data] = None # Kommentoitu, jotta aktiivista projektia ei vaihdeta, jos uusi url ei ole validi
        return False


def start_page():
    """
    Sivu sisältää syöttökentät GitLabin ja Clockifyn access tokenien sekä analysoitavan GitLab-projektin url-osoitteen määrittämiseen
    """

    col1, col2 = st.columns([1, 5])
    with col2:
        if os.path.exists("/.dockerenv"):
            image_path = "src/images/logo.png"
        else:
            image_path = "images/logo.png"

        st.image(image_path, width=500)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        load_dotenv()
        env_gitlab_token = os.getenv(gitlab_token,"")
        env_clockify_token = os.getenv(clockify_token,"")

        gitlab_token_value = st.text_input(text_gitlab_token, value = env_gitlab_token, type = "password", help = help_required)
        clockify_token_value = st.text_input(text_clockify_token, value = env_clockify_token, type = "password", help = help_optional)
        if st.button(save, help = save_help):
            if gitlab_token_value or clockify_token_value:
                # Poistetaan tiedosto, jos se on olemassa
                if os.path.exists(".env"):
                    os.remove(".env")
                # Arvot tiedostoon
                with open(".env", "w") as f:
                    if gitlab_token_value:
                        f.write(f"{gitlab_token}={gitlab_token_value}\n")
                    if clockify_token_value:
                        f.write(f"{clockify_token}={clockify_token_value}\n")
            else:
                st.error(missing_token_values, icon="❗")

        st.write("")
        st.write("")

        act_proj_url = "https://"
        if st.session_state[proj_data]:
            act_proj_url = st.session_state[proj_data].get_project_url()

        gitlab_url = st.text_input(repo_address, help = help_repo_address, value = act_proj_url)

        # Painettu Rouskuta-painiketta tai vaihdetaan projektia enteriä painamalla
        if st.button(crunch, help = help_crunch) or \
           (gitlab_url and st.session_state[proj_data] and gitlab_url != st.session_state[proj_data].get_project_url()):
            if not gitlab_url:
                st.error(missing_url, icon="❗")
            elif not gitlab_token_value:
                st.error(missing_g_token, icon="❗")
            elif not cl.validate_url(gitlab_url):
                st.error(invalid_url, icon="❗")
            else:                
                with st.spinner(fetching_data):
                    # TODO: Clockify-datan haku
                    if get_project_data(gitlab_url, gitlab_token_value):
                        st.switch_page("app_pages/project.py")
                    else:
                        st.error(error_msg, icon="❗")

start_page()