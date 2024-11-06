import streamlit as st
import pandas as pd
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
pcs = "Kpl"
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
        # Expander
        st.write("")
        st.write("")
        with st.expander(info):
            st.write(f'''
                {description}: {st.session_state[proj_data].get_description()} \n
                {creation_date}: {st.session_state[proj_data].get_creation_date()}\n
                {update_date}: {st.session_state[proj_data].get_update_date()}\n
                {namespace}: {st.session_state[proj_data].get_namespace_name()}\n
                {visibility}: {st.session_state[proj_data].get_visibility()}\n
            ''')
        
        # Donitsit
        st.markdown(f'#### {completion_status}')
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            st.write(milestones)
            milestone_donut = cl.make_donut(50, milestones, 'blue')
            st.altair_chart(milestone_donut)
        with col1_2:
            st.write(issues)
            issue_donut = cl.make_donut(40, milestones, 'blue')
            st.altair_chart(issue_donut)

    with col1:
        # Mittarit
        st.markdown(f'#### {project_metrics}')
        st.write("")
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            st.metric(milestones, st.session_state[proj_data].count_milestones())
            st.write("")
            #st.metric(work_hours, 125)
            st.metric(branches, st.session_state[proj_data].count_branches())
        with col1_2:
            st.metric(issues, st.session_state[proj_data].count_issues())
            st.write("")
            st.metric(opened_merge_requests, st.session_state[proj_data].count_open_merge_requests())

    with col3:
        # Projektiryhmä
        cl.make_team_member_selector(st.session_state[proj_data].get_assignees())

        # Palkkikaavio
        import random
        test_data = {
            "milestones": ['Sprint 1'] * 5 + ['Sprint 2'] * 5 + ['Sprint 3'] * 5 + ['Sprint 4'] * 5 + ['Sprint 5'] * 5 + ['Sprint 6'] * 5,
            "member": ['Aku', 'Hessu', 'Minni'] * 10,
            "kpl": [random.randint(20, 100) for _ in range(30)],
        }
        option1 = st.selectbox(" ",(closed_issues, commits, work_hours), label_visibility="hidden", key="datatype1")
        st.bar_chart(test_data, x="milestones", y="kpl", color="member", horizontal=True)

        # Viivakaavio
        from datetime import datetime, timedelta
        test_data2 = {
            "dates": [datetime.today() + timedelta(days=i) for i in range(30)],
            "member": ['Aku', 'Hessu', 'Minni'] * 10,
            "value": [random.randint(20, 100) for _ in range(30)],
        }
        option2 = st.selectbox(" ",(closed_issues, commits, work_hours), label_visibility="hidden", key="datatype2")
        st.line_chart(test_data2, x="dates", y="value", color="member")


cl.make_page_title(project_title)

if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    project_page()


