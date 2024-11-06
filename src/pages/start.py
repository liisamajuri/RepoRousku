import streamlit as st

# Kielikäännökset
app_title = "RepoRousku"
repo_address = "GitLab-repositorion osoite"
gitlab_token = "GitLab Access Token"
clockify_token = "Clockify Access Token"
save = "Tallenna"
crunch = "Rouskuta"
save_help = "Tallenna access tokenit. Aiemmin tallennetut access tokenit poistetaan."
help_required = "Pakollinen. Projektitietojen haku GitLabista edellyttää GitLabin access tokenia."
help_optional = "Valinnainen. Jos Clockifyn access tokenia ei määritetä, tietoja ei haeta Clockifystä."
help_repo_address = "Anna projektin päätason url"
help_crunch = "Hae projektin tiedot GitLabista"

# Muuttujat
app_logo = "✨"


def start_page():
    """
    Sivulla syöttökentät GitLabin ja Clockifyn access tokenien sekä analysoitavan GitLab-projektin url-osoitteen määrittämiseen
    """
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown(f'<h1 style="text-align: right;">{app_logo}</h1>', unsafe_allow_html=True)

    with col2:
        st.title(app_title)
        st.write("")

        gitlab_access_token = st.text_input(gitlab_token, type = "password", help = help_required)
        clockify_access_token = st.text_input(clockify_token, type = "password", help = help_optional)
        if st.button(save, help = save_help):
            pass

        st.write("")
        st.write("")

        proj_url = st.text_input(repo_address, help = help_repo_address)
        if st.button(crunch, help = help_crunch):
            pass

start_page()