"""
RepoRouskun etusivu, jonka avulla käyttäjä määrittelee tarkasteltavan projektin ja tarvittavat pääsyoikeudet projektin dataan.
Käyttäjän tulee antaa vähintään projektin GitLab-repositorion URL ja Access Token. Jos käyttäjä määrittää lisäksi 
GitLab-projektiin liittyvän Clockify-projektin ja sen Access Tokenin, on sovelluksessa mahdollista tarkastella myös 
projektin ajankäyttöä.
"""

import streamlit as st
from pathlib import Path

import libraries.components as cl
import libraries.env_tokens as et
from gitlab_api import ProjectData

# Kielikäännökset
app_title = "RepoRousku"
repo_address = "GitLab-repositorion osoite"
text_gitlab_token = "GitLab Access Token"
text_clockify_token = "Clockify Access Token"
save_tokens = "Tallenna tokenit"
remove_tokens = "Poista tallennetut tokenit"
crunch = "Rouskuta"
save_tokens_help = "Tallenna access tokenit. Aiemmin tallennetut access tokenit poistetaan."
remove_tokens_help = "Poista tallennetut access tokenit."
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


# Muuttujat
proj_data = "proj_data"
white_color = "#ffffff"


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
    Sivu sisältää syöttökentät GitLabin ja Clockifyn -projektien ja niiden access tokenien määrittämiseen
    """

    # Alustetaan session_state, jos proj_data puuttuu
    if proj_data not in st.session_state:
        st.session_state[proj_data] = None    
    
    # Otsikkorivi
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        bc = cl.get_background_color()
        if bc and bc == white_color:
            image_path = Path(__file__).parent.parent / 'images' / 'title_light.png'
        else:
            image_path = Path(__file__).parent.parent / 'images' / 'title_dark.png'
        st.image(str(image_path), width=500)

    st.write("")
    st.write("")

    col1, col2, col3, col4 = st.columns([1, 2, 1, 1]) # col1 ja col4 marginaaleja

    # Projektit
    with col2:
        act_proj_url = ""
        if st.session_state[proj_data]:
            act_proj_url = st.session_state[proj_data].get_project_url()

        gitlab_url = st.text_input(repo_address, help = help_repo_address, value = act_proj_url, placeholder = "https://")

        st.text_input("Clockify-kenttä 1", help = "testi")
        st.text_input("Clockify-kenttä 2", help = "testi")

    # Access tokenit
    with col3:
        env_gitlab_token, env_clockify_token = et.get_env_tokens()

        placeholder_g = st.empty()
        placeholder_c = st.empty()
        gitlab_token_value = placeholder_g.text_input(text_gitlab_token, value=env_gitlab_token, type = "password", help = help_required, key = "g1")
        clockify_token_value = placeholder_c.text_input(text_clockify_token, value = env_clockify_token, type = "password", help = help_optional, key = "c1")

    st.write("")
    st.write("")
    st.write("")

    # Painikkeet
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col2:
        # Rouskuta-painike
        if st.button(crunch, use_container_width = True, help = help_crunch):
            
            # Jos käyttäjä ei ole antanut access tokenia, otetaan se uudestaan ympäristöstä, jos mahdollista
            if not gitlab_token_value and env_gitlab_token:
                    gitlab_token_value = placeholder_g.text_input(text_gitlab_token, value=env_gitlab_token, type = "password", help = help_required, key = "g2")
            if not clockify_token_value and env_clockify_token:
                    clockify_token_value = placeholder_c.text_input(text_clockify_token, value=env_clockify_token, type = "password", help = help_optional, key = "c2")

            # Tarkistetaan, että tarvittavat syötteet on annettu
            if not gitlab_url:
                st.error(missing_url, icon="❗")
            elif not gitlab_token_value:
                st.error(missing_g_token, icon="❗")
            elif not cl.validate_url(gitlab_url):
                st.error(invalid_url, icon="❗")
            else:                
                with st.spinner(fetching_data):
                    # TODO: Clockify-datan haku

                    # GitLab-projektin tietojen haku
                    if get_project_data(gitlab_url, gitlab_token_value):
                        st.switch_page("app_pages/project.py")
                    else:
                        st.error(error_msg, icon="❗")
    with col3:
        # Tallenna tokenit
        if st.button(save_tokens, use_container_width = True, help = save_tokens_help):
            if gitlab_token_value or clockify_token_value:
                et.save_tokens_to_env(gitlab_token_value, clockify_token_value)
                env_gitlab_token, env_clockify_token = et.get_env_tokens()

            else:
                st.error(missing_token_values, icon="❗")
    with col4:
        # Poista tallennetut tokenit
        if st.button(remove_tokens, use_container_width = True, help = remove_tokens_help):
            et.remove_tokens_from_env_file()
            env_gitlab_token, env_clockify_token = et.get_env_tokens()


start_page()