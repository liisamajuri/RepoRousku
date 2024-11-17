"""
Projektitietojen dashboard, jonka avulla käyttäjä voi tarkastella projektin valmiusastetta, keskeisiä metriikoita, 
projektiryhmän jäseniä sekä issueita ja committeja jaoteltuina milestonejen ja jäsenten mukaan.
"""

import streamlit as st
import libraries.components as cl

# Kielikäännökset
project_title = "Projekti"
info = "Tietoja"
description = "Kuvaus"
namespace = "Nimiavaruus"
update_date = "Päivitetty viimeksi"
creation_date = "Luontipvm"
visibility = "Näkyvyys"
milestones = "Milestonet"
issues = "Issuet"
completion_status = "Projektin valmiusaste"
project_metrics = "Projektin metriikat"
work_hours = "Työtunnit"
opened_merge_requests = "Avoimet merge requestit"
closed_issues = "Suljetut issuet"
commits = "Commitit"
branches = "Branchit"

# Muuttujat
proj_data = "proj_data"

def project_page():
    """
    Sivulla esitetään projektin keskeisimmät tiedot
    """
    col1, col2, col3 = st.columns([3, 0.5, 9])

    with col1:
        
        # Donitsit
        st.markdown(f'#### {completion_status}')
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            st.write(milestones)
            milestone_donut = cl.make_donut(st.session_state[proj_data].get_readiness_ml(), milestones, 'orange')
            st.altair_chart(milestone_donut)
        with col1_2:
            st.write(issues)
            issue_donut = cl.make_donut(st.session_state[proj_data].get_readiness_issues(), issues, 'orange')
            st.altair_chart(issue_donut)

    with col1:
        # Mittarit
        st.write("")
        st.markdown(f'#### {project_metrics}')
        st.write("")
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            st.metric(milestones, st.session_state[proj_data].count_milestones())
            st.write("")
            if cl.clockify_available():
                st.metric(work_hours, 125)
            else:
                st.metric(branches, st.session_state[proj_data].count_branches())
        with col1_2:
            st.metric(issues, len(st.session_state[proj_data].get_issues()))
            st.write("")
            st.metric(opened_merge_requests, st.session_state[proj_data].count_open_merge_requests())

        # Expanderit
        st.write("")
        st.write("")
        desc = st.session_state[proj_data].get_description()
        if desc:
            with st.expander(description):
                st.write(desc)

        with st.expander(info):
            space = st.session_state[proj_data].get_namespace_name()
            project_url = st.session_state[proj_data].get_project_url()
            st.write(f'''
                {creation_date}: {st.session_state[proj_data].get_creation_date()}\n
                {update_date}: {st.session_state[proj_data].get_update_date()}\n
                {namespace}: {space if space else "-"}\n
                {visibility}: {st.session_state[proj_data].get_visibility()}\n
            ''')
            if project_url:
                st.markdown(f"**GitLab:** [Avaa projekti]({project_url})", unsafe_allow_html=True)

    with col3:
        # Projektiryhmä
        members = cl.make_team_member_selector(st.session_state[proj_data].get_assignees())

        # Välilehdet milestonekaavioihin
        tabs = [closed_issues, commits]
        if cl.clockify_available():
            tabs.append(work_hours)

        tab_objects_b = st.tabs(tabs)
        tab_b1, tab_b2 = tab_objects_b[:2]
        if cl.clockify_available():
            tab_b3 = tab_objects_b[2]

        # Suljetut issuet ja commitit milestoneittain
        with tab_b1:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_closed_issues_by_milestone(members)
            st.bar_chart(data, x=x_field, y=y_field, color=color_field, horizontal=True)
        with tab_b2:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_commits_by_milestone(members)
            st.bar_chart(data, x=x_field, y=y_field, color=color_field, horizontal=True)

        if cl.clockify_available():
            with tab_b3:
                pass # TODO: Clockify

        # Välilehdet aikasarjakaavioihin
        tab_objects_l = st.tabs(tabs)
        tab_l1, tab_l2 = tab_objects_l[:2]
        if cl.clockify_available():
            tab_l3 = tab_objects_l[2]

        # Aikasarjat suljetuista issueista ja commiteista
        with tab_l1:
            data, x_label, y_label = st.session_state[proj_data].get_closed_issues_by_date(members)
            st.bar_chart(data, x_label=x_label, y_label=y_label)
        with tab_l2:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_commits_by_date(members)
            st.bar_chart(data, x=x_field, y=y_field, color=color_field)

        if cl.clockify_available():
            with tab_l3:
                pass # TODO: Clockify


if not st.session_state[proj_data]:
    cl.make_page_title(project_title)
    cl.make_start_page_button()
else:
    cl.make_page_title(st.session_state[proj_data].get_name())
    project_page()