"""
Dashboard projektin datan tarkasteluun projektiryhmän jäsenen/jäsenten näkökulmasta. 
Dashboardin avulla yksittäinen jäsen voi koostaa tiedot issueistaan ja työtunneistaan 
projektikurssin raportointia varten.
"""

import streamlit as st
import libraries.components as cl

#Projektin linkki testausta varten: https://gitlab.dclabra.fi/projektiopinnot-4-digitaaliset-palvelut/palikkapalvelut

# Kielikäännökset
member_title = "Jäsenet"
closed_issues_title = "Suljetut issuet"
open_issues_title = "Avoimet issuet"
commits_title = "Commitit"
work_hours_title = "Työtunnit"
no_issues = "Ei issueita."
no_commits = "Ei committeja"
total_issues = "Kokonaismäärä"
titles = "Issueiden otsikot"
clockify_not_available = "Clockify-integraatio ei ole käytössä."
select_member = "Valitse jäsen projektitiimistä"
all_members = "Kaikki"

# Muuttujat
proj_data = "proj_data"

def member_page():
    """
    Sivu projektiryhmän jäseten statistiikan tarkasteluun 
    """
    st.markdown("## " + member_title)

    # Käyttäjävalinta
    selected_member = st.selectbox(select_member, [all_members] + st.session_state[proj_data].get_assignees())

    tab1, tab2 = st.tabs([closed_issues_title, open_issues_title])

    with tab1:
        # Näytä suljetut issuet
        st.markdown(f"### {closed_issues_title}")
        closed_issues = st.session_state[proj_data].get_closed_issues()

        #suodata valitun jäsenen mukaan
        if selected_member != all_members:
            closed_issues = closed_issues[closed_issues["assignees"].apply(lambda assignees: selected_member in assignees)]
        
        if closed_issues.empty:
            st.write(no_issues)

        else:
            st.write(f"{total_issues}: {len(closed_issues)}")
            st.write(f"{titles}:")
            st.dataframe(closed_issues[['title']].reset_index(drop=True), height=400)  # Vieritettävä lista otsikoista

    with tab2:
        # Näytä avoimet issuet
        st.markdown(f"### {open_issues_title}")
        open_issues = st.session_state[proj_data].get_open_issues()

        # Suodata valitun jäsenen mukaan
        if selected_member != all_members:
            open_issues = open_issues[open_issues["assignees"].apply(lambda assignees: selected_member in assignees)]

        if open_issues.empty:
            st.write(no_issues)
        else:
            st.write(f"{total_issues}: {len(open_issues)}")
            st.write(f"{titles}:")
            st.dataframe(open_issues[['title']].reset_index(drop=True), height=400)  # Vieritettävä lista otsikoista



    col1, col2 = st.columns([3, 7])

    with col1:
        # Näytä kommittien kokonaismäärä
        st.markdown(f"### {commits_title}")
        commits = st.session_state[proj_data].get_commits()

        # Suodata valitun jäsenen mukaan
        if selected_member != all_members:
            commits = commits[commits["author_name"].apply(lambda author_name: select_member in author_name)]
        
        if commits.empty:
            st.write(no_commits)
        
        else:
            st.write(f"{commits}: {len(commits)}") #Committien kokonaismäärä

    with col2:
        # TODO: Näytä tuntien kokonaismäärä (jos Clockify käytössä) + piirakkadiagrammi 
        # + suodatus valitun käyttäjän mukaan
        if cl.clockify_available():
            st.markdown(f"### {work_hours_title}")
            total_hours = st.session_state[all_user_hours].get_all_user_hours_df(st.session_state[proj_data].get_id())['Työtunnit'].sum()
            st.write(f"{total_issues}: {total_hours:.2f} h")
        else:
            st.write(clockify_not_available)

# Sivun otsikko ja mahdollinen navigaatio aloitussivulle
cl.make_page_title(gitlab_title)
if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    member_page()
