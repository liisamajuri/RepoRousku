import streamlit as st
import libraries.components as cl
import pandas as pd

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
            if False: # TODO: Jos clockify liitetty, näytetään työtunnit branchien sijaan
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
            st.write(f'''
                {creation_date}: {st.session_state[proj_data].get_creation_date()}\n
                {update_date}: {st.session_state[proj_data].get_update_date()}\n
                {namespace}: {space if space else "-"}\n
                {visibility}: {st.session_state[proj_data].get_visibility()}\n
            ''')

    with col3:
        # Projektiryhmä
        members = cl.make_team_member_selector(st.session_state[proj_data].get_assignees())

        # Datavalitsin palkkikaavioon
        if False:
            options = (closed_issues, commits, work_hours)
        else:
            options = (closed_issues, commits)

        # Datatyypin valinta palkkikaavioon
        col3_1, col3_2 = col3.columns([1, 5])
        with col3_1:
            option_bar = st.selectbox(" ", options, label_visibility="hidden", key="datatype1")

        # Palkkikaavio

        if option_bar == closed_issues:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_data_for_closed_issues_bar_chart(members)

        elif option_bar == commits:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_data_for_commits_bar_chart(members)

        else:
            # TODO: Clockify-tunnit
            pass

        st.bar_chart(data, x=x_field, y=y_field, color=color_field, horizontal=True)

        # Datatyypin valinta viivakaavioon
        col3_1, col3_2 = col3.columns([1, 5])
        with col3_1:
            option_line = st.selectbox(" ",options, label_visibility="hidden", key="datatype2", index=1)

        # Viivakaavio

        if option_line == closed_issues:
            data = st.session_state[proj_data].get_data_for_closed_issues_line_chart(members)
            st.line_chart(data)

        elif option_line == commits:
            data, x_field, y_field, color_field = st.session_state[proj_data].get_data_for_commits_line_chart(members)
            st.line_chart(data, x=x_field, y=y_field, color=color_field)

        else:
            # TODO: Clockify-tunnit
            pass

if not st.session_state[proj_data]:
    cl.make_page_title(project_title)
    cl.make_start_page_button()
else:
    cl.make_page_title(st.session_state[proj_data].get_name())
    project_page()