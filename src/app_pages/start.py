"""
RepoRouskun etusivu, jonka avulla käyttäjä määrittelee tarkasteltavan projektin ja tarvittavat pääsyoikeudet projektin dataan.
Käyttäjän tulee antaa vähintään projektin GitLab-repositorion URL ja Access Token. Jos käyttäjä määrittää lisäksi 
GitLab-projektiin liittyvän Clockify-projektin  Access Tokenin, on sovelluksessa mahdollista tarkastella myös 
projektin ajankäyttöä.
"""

import streamlit as st
from pathlib import Path

import libraries.components as cl
from gitlab_api import ProjectData
from clockify_api import ClockifyData
import os

# Kielikäännökset
app_title = "RepoRousku"
repo_address = "GitLab-repositorion osoite"
text_gitlab_token = "GitLab Access Token"
text_clockify_token = "Clockify Access Token"
save_tokens = "Tallenna tokenit istunnon ajaksi"
remove_tokens = "Poista tallennetut tokenit"
crunch = "Rouskuta"
save_tokens_help = "Tallenna access tokenit istunnon ajaksi. Aiemmin tallennetut access tokenit poistetaan."
remove_tokens_help = "Poista tallennetut access tokenit"
help_required = "Pakollinen. Projektitietojen haku GitLabista edellyttää GitLabin access tokenia."
help_optional = "Valinnainen. Jos Clockifyn access tokenia ei määritetä, tietoja ei haeta Clockifystä."
help_repo_address = "Anna projektin päätason url"
help_crunch = "Hae projektin tiedot"
fetching_data = "Haetaan tietoja..."
missing_g_token = "GitLab Access Token puuttuu!"
missing_url = "GitLab-projektin osoite puuttuu!"
invalid_url = "Virheellinen GitLab-projektin osoite!"
error_msg = "Tarkista GitLab-osoite ja Access Token!"
missing_token_values = "Access Token(it) puuttuu!"
tokens_saved = "Token(it) tallennettu."
tokens_removed = "Token(it) poistettu."


# Muuttujat
proj_data = "proj_data"
white_color = "#ffffff"
clockify_workspace = "clockify_workspace"
clockify_project = "clockify_project"
gitlab_token_key = "gitlab_token"
clockify_token_key = "clockify_token"


def setup_clockify(clockify_token):
    """
    Asettaa Clockify-muuttujiin arvot.

    Args:
        clockify_token (str): Clockifyn Access Token.

    Returns:
        (ClockiFy): Clockifyn tiedot sisältävä olio tai None.
    """
    if clockify_token:
        os.environ["CLOCKIFY_TOKEN"] = clockify_token 
        clockify = ClockifyData("https://api.clockify.me/api/v1")
        return clockify
    else:
        st.error("Clockify Token puuttuu!", icon="❗")
        return None


def fetch_clockify_data(clockify):
    """
    Hakee Clockify-datan, projektin työtunnit ja tallentaa ne session_stateen.

    Args:
        clockify (ClockiFy): ClockiFy-olio.

    Returns:
        (DataFrame): Clockifyyn kirjatut työtunnit.
    """
    if clockify:
        try:
            # Haetaan työtilat Clockify API:sta
            workspaces = clockify.get_workspaces()
            if not workspaces:
                st.warning("Ei löytynyt työtiloja Clockifystä.")
                return None
            workspace_options = [ws["name"] for ws in workspaces]
            selected_workspace = st.selectbox("Valitse työtila", workspace_options)
            selected_workspace_id = next(ws["id"] for ws in workspaces if ws["name"] == selected_workspace)
            clockify.workspace_id = selected_workspace_id  
            projects = clockify.get_projects()
            if projects:
                project_options = [project["name"] for project in projects]
                selected_project = st.selectbox("Valitse projekti", project_options)
                selected_project_id = next(proj["id"] for proj in projects if proj["name"] == selected_project)
                clockify.project_id = selected_project_id
                all_user_hours = clockify.get_all_user_hours_df()
                if not all_user_hours.empty:
                    st.session_state["clockify_data"] = all_user_hours
                    st.session_state[clockify_workspace] = selected_workspace_id
                    st.session_state[clockify_project] = selected_project_id
                    st.success("Clockify-data haettu onnistuneesti!")
                    return all_user_hours
                else:
                    st.warning("Ei löytynyt työtunteja projektista.")
            else:
                st.warning("Ei löytynyt projekteja valitusta työtilasta.")
                return None
        except Exception as e:
            st.error(f"Virhe Clockify-datan hakemisessa: {str(e)}", icon="❗")
            return None
    else:
        st.error("Clockify Token puuttuu!", icon="❗")
        return None


def fetch_sprint_hours(clockify, gitlab_url, gitlab_token):
    """
    Hakee ja tallentaa sprinteittäin kertyneet työtunnit session_stateen.

    Args:
        clockify (ClockiFy): ClockiFy-olio.
        gitlab_url (str): Projektin GitLab url.
        gitlab_token (str): Projektin GitLabin Access Token.
    """
    sprint_hours_df_grouped = clockify.get_sprint_hours(gitlab_url, gitlab_token)
    if not sprint_hours_df_grouped.empty:
        st.session_state["sprint_hours_df_grouped"] = sprint_hours_df_grouped
    else:
        st.warning("Sprinttien työtunteja ei löytynyt.")


def fetch_sprint_and_tag_hours(clockify, gitlab_url, gitlab_token):
    """
    Hakee ja tallentaa sprinteittäin ja tageittain kertyneet työtunnit session_stateen.

    Args:
        clockify (ClockiFy): ClockiFy-olio.
        gitlab_url (str): Projektin GitLab url.
        gitlab_token (str): Projektin GitLabin Access Token
    """
    sprint_and_tag_hours_df = clockify.get_project_tag_and_sprint_hours(gitlab_url, gitlab_token)
    if not sprint_and_tag_hours_df.empty: 
        st.session_state["sprint_and_tag_hours"] = sprint_and_tag_hours_df
    else:
        st.warning("Sprinttien ja tagien työtunteja ei löytynyt.")



def get_project_data(gitlab_url, gitlab_token):
    """
    Hakee datan GitLab-projektista.

    Args:
        gitlab_url (str): Projektin GitLab url.
        gitlab_token (str): GitLab Access Token.
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
    Moduulin pääkoodilohko, joka muodostaa sivun projektin GitLab-osoitteen ja tarvittavien Access Tokenien määrittelyyn.
    """
    # Alustetaan session_state, jos proj_data puuttuu
    if proj_data not in st.session_state:
        st.session_state[proj_data] = None
    if clockify_workspace not in st.session_state:
        st.session_state[clockify_workspace] = None
    if clockify_project not in st.session_state:
        st.session_state[clockify_project] = None
    if gitlab_token_key not in st.session_state:
        st.session_state[gitlab_token_key] = ""
    if clockify_token_key not in st.session_state:
        st.session_state[clockify_token_key] = ""

    
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


    # Access tokenit
    with col3:
        placeholder_g = st.empty()
        placeholder_c = st.empty()
        gitlab_token_value = placeholder_g.text_input(text_gitlab_token, value=st.session_state[gitlab_token_key], type = "password", help = help_required, key = "g1")
        clockify_token_value = placeholder_c.text_input(text_clockify_token, value = st.session_state[clockify_token_key], type = "password", help = help_optional, key = "c1")
        # Linkki ohjeseen
        st.markdown("[Katso Ohje](https://gitlab.dclabra.fi/wiki/MOpevPu-QrClH4_ouAV04A?view)", unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")

    if clockify_token_value:
        with col2:
            clockify = setup_clockify(clockify_token_value)
            fetch_clockify_data(clockify)

    # Painikkeet
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    with col2:
        # Rouskuta-painike
        if st.button(crunch, use_container_width = True, help = help_crunch):
            
            # Jos käyttäjä ei ole antanut access tokenia, otetaan se session statesta, jos mahdollista
            if not gitlab_token_value and st.session_state[gitlab_token_key]:
                    gitlab_token_value = placeholder_g.text_input(text_gitlab_token, value=st.session_state[gitlab_token_key], type = "password", help = help_required, key = "g2")
            if not clockify_token_value and st.session_state[clockify_token_key]:
                    clockify_token_value = placeholder_c.text_input(text_clockify_token, value=st.session_state[clockify_token_key], type = "password", help = help_optional, key = "c2")

            # Tarkistetaan, että tarvittavat syötteet on annettu
            if not gitlab_url:
                st.error(missing_url, icon="❗")
            elif not gitlab_token_value:
                st.error(missing_g_token, icon="❗")
            elif not cl.validate_url(gitlab_url):
                st.error(invalid_url, icon="❗")
            else:                
                with st.spinner(fetching_data):
                    

                    # GitLab-projektin tietojen haku
                    if get_project_data(gitlab_url, gitlab_token_value):
                        # Clockify-datan haku
                        if clockify_token_value:
                            fetch_sprint_hours(clockify, gitlab_url, gitlab_token_value)
                            fetch_sprint_and_tag_hours(clockify, gitlab_url, gitlab_token_value)
                        st.switch_page("app_pages/project.py")
                    else:
                        st.error(error_msg, icon="❗")
    with col3:
        # Tallenna tokenit
        if st.button(save_tokens, use_container_width = True, help = save_tokens_help, disabled=False):
            if gitlab_token_value or clockify_token_value:
                if gitlab_token_value:
                    st.session_state[gitlab_token_key] = gitlab_token_value
                if clockify_token_value:
                    st.session_state[clockify_token_key] = clockify_token_value
                st.success(tokens_saved)
            else:
                st.error(missing_token_values, icon="❗")
    with col4:
        # Poista tallennetut tokenit
        if st.button(remove_tokens, use_container_width = True, help = remove_tokens_help, disabled=False):
            st.session_state[gitlab_token_key] = ""
            st.session_state[clockify_token_key] = ""
            #gitlab_token_value = "" # Kommentissa, koska kentän arvoa ei haluta tyhjentää
            #clockify_token_value = "" # Kommentissa, koska kentän arvoa ei haluta tyhjentää
            st.success(tokens_removed)


start_page()