"""
RepoRouskun pääohjelma, joka luo sovelluksen toimintovalikon ja avaa etusivun.
"""

import streamlit as st

# Kielikäännökset
app_title = "RepoRousku"
reports = "Raportit"
connections = "Yhteydet"
change_project = "Vaihda projekti"
open_gitlab = "Avaa GitLab"
project = "Projekti"
member = "Jäsenet"

# Muuttujat
proj_data = "proj_data"


# Tallennuspaikka projektin datalle
if proj_data not in st.session_state:
    st.session_state[proj_data] = None


def set_appearance():
    """
    Määrittää sovelluksen ulkoasun.
    """
    st.set_page_config(
        page_title = app_title,
        page_icon = "🍄",
        layout = 'wide',
        initial_sidebar_state = "collapsed"
    )


def create_navigation_panel():
    """
    Luo navigointivalikon sivustorakenteesta.
    """
    # Navigointivalikko
    app_pages = {
        connections: [
            st.Page("app_pages/start.py", title=change_project, icon = "🔄", default=True),
        ],
        reports: [
            st.Page("app_pages/project.py", title=project, icon = "📈"),
            st.Page("app_pages/members.py", title=member, icon = "🙋🏻‍♂️")
        ],
    }

    project_url = None
    if proj_data in st.session_state and st.session_state[proj_data] is not None:
        project_url = st.session_state[proj_data].get_project_url()

    if project_url:
        with st.sidebar:
            st.markdown(
                f"🔗 [{open_gitlab}]({project_url})",
                unsafe_allow_html=True
            )

    pg = st.navigation(app_pages)
    pg.run()


def main():
    """
    Sovelluksen pääohjelma.
    """
    set_appearance()
    create_navigation_panel()


main()