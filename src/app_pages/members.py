"""
Dashboard projektin datan tarkasteluun projektiryhmän jäsenen/jäsenten näkökulmasta. 
Dashboardin avulla yksittäinen jäsen voi koostaa tiedot issueistaan ja työtunneistaan 
projektikurssin raportointia varten.
"""

import streamlit as st
from pathlib import Path
import libraries.components as cl
import plotly.express as px
import numpy as np


# Kielikäännökset
member_title = "Jäsenet"
issues_title = "Issuet"
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
select_milestone = "Valitse milestonet"
commits = "Commitit"
all_members = "Kaikki"

# Muuttujat
proj_data = "proj_data"
white_color = "#ffffff"

def member_page():
    """
    Sivu projektiryhmän jäsenten statistiikan tarkasteluun.

    Tietoja on mahdollista suodattaa valitsemalla tarkasteltavat milestonet sekä projektiryhmän
    yksi jäsen / kaikki jäsenet. Dashboardilla esitetään listaukset issueista, keskeisimmät
    työskentelyn metriikat ja myös työtunnit, mikäli Clockify-integraatio on käytössä.
    """
    # Tarkista, että proj_data on määritelty sessiossa ennen projektin nimen näyttämistä
    project_title = st.session_state[proj_data].get_name() if proj_data in st.session_state else "Projekti"

    # Näytä projektin nimi 
    cl.make_page_title(member_title, project_title)
    
    # Valinnat
    col1, col_empty, col2 = st.columns([2, 0.1, 3])

    # Käyttäjävalinta
    with col1: 
        selected_member = st.selectbox(select_member, [all_members] + st.session_state[proj_data].get_assignees())

    # Milestone-valinta
    with col2:
        milestones = st.session_state[proj_data].get_milestones()
        milestone_options = milestones['title'].tolist() if not milestones.empty else []
        selected_milestones = st.pills(
            select_milestone,
            options=milestone_options,
            selection_mode = 'multi',
            default = milestone_options
        )

    # Ensimmäinen kolumni: suljetut/avoimet issuet välilehtinä
    with col1:
        st.markdown(f"### {issues_title}")

        tab1, tab2 = st.tabs([closed_issues_title, open_issues_title])

        with tab1:
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
                    height=400,
                    use_container_width=True
                )

        with tab2:
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
                    height=400,
                    use_container_width=True
                )

    # Toinen kolumni: kommittien ja issueiden lukumäärät laatikossa
    col2_1, col2_2 = col2.columns([1, 3])
    
    with col2_1:
        st.markdown(f"### {metrics_title}")
        st.write("")
        st.write("")

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
        st.write("")

        # Suljetut issuet valitun jäsenen ja milestonejen mukaan
        closed_issues = st.session_state[proj_data].get_closed_issues()
        if selected_member != all_members:
            closed_issues = closed_issues[closed_issues["assignees"].apply(lambda assignees: selected_member in assignees)]
        if selected_milestones:
            closed_issues = closed_issues[closed_issues["milestone"].isin(selected_milestones)]

        # Näytä suljettujen issueiden määrä
        st.metric(closed_issues_title, len(closed_issues))
        st.write("")

        # Avoimet issuet valitun jäsenen ja milestonejen mukaan
        open_issues = st.session_state[proj_data].get_open_issues()
        if selected_member != all_members:
            open_issues = open_issues[open_issues["assignees"].apply(lambda assignees: selected_member in assignees)]

        if selected_milestones:
            open_issues = open_issues[open_issues["milestone"].isin(selected_milestones)]

        # Näytä avointen issueiden määrä
        st.metric(open_issues_title, len(open_issues))
        st.write("")


    # Kolmas kolumni: tuntitiedot ja piirakkadiagrammi
        with col2_2:
            st.markdown(f"### {work_hours_title}")

            if cl.clockify_available():
                total_hours = 0

                if 'sprint_hours_df_grouped' in st.session_state:
                    sprint_hours_df_grouped = st.session_state['sprint_hours_df_grouped']
                    if selected_member != all_members:
                        filtered_df = sprint_hours_df_grouped[
                            (sprint_hours_df_grouped['user'] == selected_member) &
                            (sprint_hours_df_grouped['milestone'].isin(selected_milestones))
                        ]
                    else:
                        filtered_df = sprint_hours_df_grouped[
                            sprint_hours_df_grouped['milestone'].isin(selected_milestones)
                        ]
                    if not filtered_df.empty:
                        total_hours = filtered_df['total_hours'].sum()
                if "sprint_and_tag_hours" in st.session_state:
                    sprint_tag_hours_df = st.session_state["sprint_and_tag_hours"]
                    if selected_member != all_members:
                        filtered_tag_df = sprint_tag_hours_df[
                            (sprint_tag_hours_df['user_name'] == selected_member) &
                            (sprint_tag_hours_df['milestone'].isin(selected_milestones))
                        ]
                    else:
                        filtered_tag_df = sprint_tag_hours_df[
                            sprint_tag_hours_df['milestone'].isin(selected_milestones)
                        ]

                    if not filtered_tag_df.empty:
                        tag_hours_df = filtered_tag_df.groupby('tag')['total_tag_hours'].sum().reset_index()

                        if not tag_hours_df.empty:
                            fig = px.pie(
                            tag_hours_df,
                            names='tag',
                            values='total_tag_hours',
                            title=f"Työaika tageittain: {selected_member}",
                            labels={'tag': 'Tagi', 'total_tag_hours': 'Tunnit'}
                        )
                        st.plotly_chart(fig)
                    else:
                        st.write("Ei tagitietoja saatavilla.")
                with col2_1:
                    st.metric(work_hours_title, np.round(total_hours).astype(int))

            else:
                with col2_2:
                # näytä logo, jos Clockify-data ei ole saatavilla
                    bc = cl.get_background_color()
                    if bc and bc == white_color:
                        image_path = Path(__file__).parent.parent / 'images' / 'mushroom_light.png'

                    else:
                        image_path = Path(__file__).parent.parent / 'images' / 'mushroom_dark.png'
                    st.image(str(image_path), caption=clockify_not_available)

# Sivun otsikko 
if not st.session_state[proj_data]:
    cl.make_page_title(member_title)
    cl.make_start_page_button()
else:
    member_page()

