"""
Dashboard projektin datan tarkasteluun projektiryhmän jäsenen/jäsenten näkökulmasta. 
Dashboardin avulla yksittäinen jäsen voi koostaa tiedot issueistaan ja työtunneistaan 
projektikurssin raportointia varten.
"""

import streamlit as st
import libraries.components as cl

# Kielikäännökset
member_title = "Jäsenet"
closed_issues_title = "Suljetut issuet"
commits_title = "Commitit"
work_hours_title = "Työtunnit"
no_issues = "Ei suljettuja issueita."
total_issues = "Kokonaismäärä"
titles = "Otsikot"
clockify_not_available = "Clockify-integraatio ei ole käytössä."

# Muuttujat
proj_data = "proj_data"

def member_page():
    """
    Sivu projektiryhmän jäseten statistiikan tarkasteluun (MVP)
    """
    st.markdown("## " + member_title)

    # Käyttäjävalinta
    selected_members = cl.make_team_member_selector(st.session_state[proj_data].get_assignees())

    # Kahden kolumnin layout
    col1, col2 = st.columns(2)

    with col1:
        # Näytä suljettujen issueiden määrä ja vieritettävä lista otsikoista
        st.markdown(f"### {closed_issues_title}")
        closed_issues = st.session_state[proj_data].get_closed_issues()
        if closed_issues.empty:
            st.write(no_issues)
        else:
            st.write(f"{total_issues}: {len(closed_issues)}")
            st.write(f"{titles}:")
            st.dataframe(closed_issues[['title']].reset_index(drop=True), height=200)  # Vieritettävä lista otsikoista

    with col2:
        # Näytä kommittien kokonaismäärä
        st.markdown(f"### {commits_title}")
        commits = st.session_state[proj_data].get_commits()
        st.write(f"{total_issues}: {len(commits)}")

        # Näytä tuntien kokonaismäärä (jos Clockify käytössä)
        if cl.clockify_available():
            st.markdown(f"### {work_hours_title}")
            total_hours = st.session_state[proj_data].get_all_user_hours_df(st.session_state[proj_data].get_id())['Työtunnit'].sum()
            st.write(f"{total_issues}: {total_hours:.2f} h")
        else:
            st.write(clockify_not_available)

# Sivun otsikko ja mahdollinen navigaatio aloitussivulle
cl.make_page_title(member_title)
if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    member_page()
