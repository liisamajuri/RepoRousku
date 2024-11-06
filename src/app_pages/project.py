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
pull_requests = "Avoimet pull requestit"
pcs = "Kpl"
closed_issues = "Suljetut issuet"
commits = "Commitit"


def project_page():
    """
    Sivulla esitetään projektin keskeisimmät tiedot
    """
    cl.make_page_title(project_title)

    col1, col2, col3 = st.columns([3, 0.5, 9])

    with col1:
        # Expander
        st.write("")
        st.write("")
        with st.expander(info):
            st.write(f'''
                {description}: \n
                {creation_date}: \n
                {update_date}: \n
                {namespace}: \n
                {visibility}: \n
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
            st.metric(milestones, 7)
            st.write("")
            st.metric(work_hours, 125)
        with col1_2:
            st.metric(issues, 46)
            st.write("")
            st.metric(pull_requests, 0)

    with col3:
        # Projektiryhmä
        cl.make_team_member_selector(["Aku Ankka","Hessu Hopo","Minni Hiiri"])

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

project_page()