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
open_issues_title = "Avoimet issuet"
commits_title = "Commitit"
work_hours_title = "Työtunnit"
no_issues = "Ei issueita."
no_commits = "Ei committeja."
total = "Kokonaismäärä"
titles = "Issueiden otsikot"
clockify_not_available = "Clockify-integraatio ei ole käytössä."
select_member = "Valitse jäsen projektitiimistä"
all_members = "Kaikki"

# Muuttujat
proj_data = "proj_data"

def member_page():
    """
    Sivu projektiryhmän jäsenten statistiikan tarkasteluun
    """
    # Tarkista, että proj_data on määritelty sessiossa ennen projektin nimen näyttämistä
    project_title = st.session_state[proj_data].get_name() if proj_data in st.session_state else "Projekti"

    # Näytä projektin nimi ja jäsenet-osio
    st.markdown(f"## {project_title}")
    
    # Käyttäjävalinta
    selected_member = st.selectbox(select_member, [all_members] + st.session_state[proj_data].get_assignees())

    col1, col2, col3 = st.columns([3, 1, 2])

    # Ensimmäinen kolumni: suljetut/avoimet issuet välilehtinä
    with col1:
        tab1, tab2 = st.tabs([closed_issues_title, open_issues_title])

        with tab1:
            st.markdown(f"### {closed_issues_title}")
            closed_issues = st.session_state[proj_data].get_closed_issues()

            # Suodata valitun jäsenen mukaan
            if selected_member != all_members:
                closed_issues = closed_issues[closed_issues["assignees"].apply(lambda assignees: selected_member in assignees)]

            if closed_issues.empty:
                st.write(no_issues)
            else:
                st.dataframe(
                    closed_issues[['title', 'milestone']].rename(
                        columns={'title': 'Otsikko', 'milestone': 'Milestone'}
                    ).reset_index(drop=True),
                    height=400
                )

        with tab2:
            st.markdown(f"### {open_issues_title}")
            open_issues = st.session_state[proj_data].get_open_issues()

            # Suodata valitun jäsenen mukaan
            if selected_member != all_members:
                open_issues = open_issues[open_issues["assignees"].apply(lambda assignees: selected_member in assignees)]

            if open_issues.empty:
                st.write(no_issues)
            else:
                st.dataframe(
                    open_issues[['title', 'milestone']].rename(
                        columns={'title': 'Otsikko', 'milestone': 'Milestone'}
                    ).reset_index(drop=True),
                    height=400
                )

    # Toinen kolumni: kommittien ja issueiden tietolaatikot
    with col2:
        st.markdown(f"### {commits_title}")
        commits = st.session_state[proj_data].get_commits()

        # Suodata valitun jäsenen mukaan
        if selected_member != all_members:
            commits = commits[commits["author_name"] == selected_member]

        if commits.empty:
            st.metric("Commitit", 0)
        else:
            st.metric("Commitit", len(commits))

        # Suljetut ja avoimet issuet
        closed_count = len(st.session_state[proj_data].get_closed_issues())
        open_count = len(st.session_state[proj_data].get_open_issues())

        st.metric("Suljetut issuet", closed_count)
        st.metric("Avoimet issuet", open_count)

    # Kolmas kolumni: tuntitiedot ja piirakkadiagrammi (myöhemmin)
    with col3:
        if cl.clockify_available():
            st.markdown(f"### {work_hours_title}")
            total_hours = st.session_state[proj_data].get_all_user_hours_df(st.session_state[proj_data].get_id())['Työtunnit'].sum()
            st.metric("Työtunnit", f"{total_hours:.2f} h")
            # TODO: Lisää piirakkadiagrammi myöhemmin
        else:
            st.write(clockify_not_available)

# Sivun otsikko ja mahdollinen navigaatio aloitussivulle
cl.make_page_title(member_title)
if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    member_page()

