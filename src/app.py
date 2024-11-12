"""
RepoRouskun pääohjelma, joka luo sovelluksen toimintovalikon ja avaa etusivun.
"""

import streamlit as st

import libraries.components as cl

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
    Määrittää sovelluksen ulkoasun
    """
    st.set_page_config(
        page_title = app_title,
        page_icon = "✨",
        layout = 'wide',
        initial_sidebar_state = "collapsed"
    )


def create_navigation_panel():
    """
    Luo navigointivalikon sivustorakenteesta
    """
    # Navigointivalikko
    app_pages = {
        connections: [
            st.Page("app_pages/start.py", title=change_project, icon = "📁", default=True),
        ],
        reports: [
            st.Page("app_pages/project.py", title=project, icon = "📊"),
            st.Page("app_pages/members.py", title=member, icon = "👤")
        ],
    }

    if not cl.in_docker():
        app_pages[connections].append(st.Page("app_pages/gitlab_link.py", title=open_gitlab, icon="🔗"))

    pg = st.navigation(app_pages)
    pg.run()


def main():
    """
    Sovelluksen pääohjelma
    """
    set_appearance()
    create_navigation_panel()


main()