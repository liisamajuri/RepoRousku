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
metrics_title = "Metriikat"
work_hours_title = "Työtunnit"
no_issues = "Ei issueita."
no_commits = "Ei committeja."
total = "Kokonaismäärä"
titles = "Issueiden otsikot"
clockify_not_available = "Clockify-integraatio ei ole käytössä."
select_member = "Valitse jäsen projektitiimistä"
select_milestone = "Valitse milestone"
commits = "Commitit"
all_members = "Kaikki"

# Muuttujat
proj_data = "proj_data"

def member_page():
    """
    Sivu projektiryhmän jäsenten statistiikan tarkasteluun
    """
    # Tarkista, että proj_data on määritelty sessiossa ennen projektin nimen näyttämistä
    project_title = st.session_state[proj_data].get_name() if proj_data in st.session_state else "Projekti"

    # Näytä projektin nimi 
    st.markdown(f"## {project_title}")
    
    # Valinnat
    col1, col2 = st.columns([1, 1])
    
    # Käyttäjävalinta
    with col1: 
        selected_member = st.selectbox(select_member, [all_members] + st.session_state[proj_data].get_assignees())

    # Milestone-valinta
    with col2:
        milestones = st.session_state[proj_data].get_milestones()
        milestone_options = milestones['title'].tolist() if not milestones.empty else []
        selected_milestones = st.multiselect(
            select_milestone,
            options=milestone_options,
            default=milestone_options
        )

    col1, col2, col3 = st.columns([2, 1, 1.5])

    # Ensimmäinen kolumni: suljetut/avoimet issuet välilehtinä
    with col1:
        tab1, tab2 = st.tabs([closed_issues_title, open_issues_title])

        with tab1:
            st.markdown(f"### {closed_issues_title}")
            closed_issues = st.session_state[proj_data].get_closed_issues()
           

            # Suodata valitun jäsenen mukaan
            if selected_member != all_members:
                closed_issues = closed_issues[closed_issues["assignees"].apply(lambda assignees: selected_member in assignees)]
            
            # Suodata valittujen milestonien mukaan
            if selected_milestones:
                closed_issues = closed_issues[closed_issues["milestone"].isin(selected_milestones)]

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

            # Suodata valittujen milestonien mukaan
            if selected_milestones:
                open_issues = open_issues[open_issues["milestone"].isin(selected_milestones)]


            if open_issues.empty:
                st.write(no_issues)
            else:
                st.dataframe(
                    open_issues[['title', 'milestone']].rename(
                        columns={'title': 'Otsikko', 'milestone': 'Milestone'}
                    ).reset_index(drop=True),
                    height=400
                )

    # Toinen kolumni: kommittien ja issueiden lukumäärät laatikossa
    with col2:
        st.markdown(f"### {metrics_title}")

        # Suodata valitun jäsenen mukaan ja valittujen milestonejen mukaan
        if selected_member != all_members:
            member_list = [selected_member]
        
        else:
            member_list = st.session_state[proj_data].get_assignees()

        commit_data, _, _, _ = st.session_state[proj_data].get_commits_by_milestone(member_list)
        
        # Suodata 
        if selected_milestones:
            commit_data = commit_data[commit_data["milestone"].isin(selected_milestones)]

        total_commits = commit_data["kpl"].sum() if not commit_data.empty else 0
        st.metric(commits, total_commits)

        # Suljetut issuet valitun jäsenen ja milestonejen mukaan
        closed_issues = st.session_state[proj_data].get_closed_issues()
        if selected_member != all_members:
            closed_issues = closed_issues[closed_issues["assignees"].apply(lambda assignees: selected_member in assignees)]
        if selected_milestones:
            closed_issues = closed_issues[closed_issues["milestone"].isin(selected_milestones)]

        # Näytä suljettujen issueiden määrä
        st.metric(closed_issues_title, len(closed_issues))

        # Avoimet issuet valitun jäsenen ja milestonejen mukaan
        open_issues = st.session_state[proj_data].get_open_issues()
        if selected_member != all_members:
            open_issues = open_issues[open_issues["assignees"].apply(lambda assignees: selected_member in assignees)]

        if selected_milestones:
            open_issues = open_issues[open_issues["milestone"].isin(selected_milestones)]

        # Näytä avointen issueiden määrä
        st.metric(open_issues_title, len(open_issues))


    # Kolmas kolumni: tuntitiedot ja piirakkadiagrammi (tulee myöhemmin)
    with col3:
        if cl.clockify_available():
            st.markdown(f"### {work_hours_title}")
            total_hours = st.session_state[proj_data].get_all_user_hours_df(st.session_state[proj_data].get_id())['Työtunnit'].sum()
            
            # TODO: Lisää tuntien suodatus milestonejen mukaan, jos mahdollista
            st.metric(work_hours_title, f"{total_hours:.2f} h")
            # TODO: Lisää piirakkadiagrammi myöhemmin
        else:
            st.write(clockify_not_available) #TODO: Tähän RepoRouskun logo jos ei näytettävää dataa

# Sivun otsikko 
cl.make_page_title(member_title)
if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    member_page()

