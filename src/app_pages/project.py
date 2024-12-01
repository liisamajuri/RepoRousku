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
completion_status = "Valmiusaste"
project_metrics = "Metriikat"
work_hours = "Työtunnit"
opened_merge_requests = "Avoimet merge requestit"
closed_issues = "Suljetut issuet"
commits = "Commitit"
branches = "Branchit"
time_period = "Milestonet"
open_issues = "Avoimet issuet"
start_txt = "alku"
end_txt = "loppu"
slider_help = "Valitse tarkasteltavan ajanjakson alku ja loppu. Ajanjakso sisältää aina vain kokonaisia milestoneja."

# Muuttujat
proj_data = "proj_data"
clockify_data = st.session_state.get('clockify_data')


def milestone_donut():
    """
    Donitsikaavio päättyneistä milestoneista suhteessa projektin kaikkiin milestoneihin.
    """
    st.write(milestones)
    milestone_donut = cl.make_donut(st.session_state[proj_data].get_readiness_ml(), milestones, 'blue')
    st.altair_chart(milestone_donut)


def issues_donut():
    """
    Donitsikaavio suljetuista issueista suhteessa projektin kaikkiin issueisiin.
    """
    st.write(issues)
    issue_donut = cl.make_donut(st.session_state[proj_data].get_readiness_issues(), issues, 'blue')
    st.altair_chart(issue_donut)


def milestone_metric():
    """
    Metriikka projektin milesonejen kokonaismäärästä.
    """
    st.metric(milestones, st.session_state[proj_data].count_milestones())


def merge_request_metric():
    """
    Metriikka projektin avoimien merge requestien määrästä.
    """
    st.metric(opened_merge_requests, st.session_state[proj_data].count_open_merge_requests())


def branch_metric():
    """
    Metriikka projektin branchien määrästä.
    """
    st.metric(branches, st.session_state[proj_data].count_branches())


def issues_metric():
    """
    Metriikka projektin issueiden kokonaismäärästä.
    """
    st.metric(issues, len(st.session_state[proj_data].get_issues()))


def open_issues_metric():
    """
    Metriikka projektin avoimien issueiden määrästä.
    """
    st.metric(open_issues, st.session_state[proj_data].count_open_issues())


def work_hours_metric():
    """
    Metriikka projektin työtuntien kokonaismäärästä.
    """
    if cl.clockify_available() and 'clockify_data' in st.session_state:
        user_hours_df = st.session_state['clockify_data']
        if not user_hours_df.empty:
            total_project_time = user_hours_df[work_hours].sum()
            total_project_time = int(total_project_time)
            st.metric(work_hours, total_project_time)
        else:
            st.warning("Ei löytynyt työtunteja.")


def project_description_expander():
    """
    Projektin kuvauksen sisältävä komponentti.
    """
    desc = st.session_state[proj_data].get_description()
    if desc:
        with st.expander(description):
            st.write(desc)


def project_info_expander():
    """
    Projektin perustiedot sisältävä komponentti.
    """
    with st.expander(info):
        space = st.session_state[proj_data].get_namespace_name()
        st.write(f'''
            {creation_date}: {st.session_state[proj_data].get_creation_date()}\n
            {update_date}: {st.session_state[proj_data].get_update_date()}\n
            {namespace}: {space if space else "-"}\n
            {visibility}: {st.session_state[proj_data].get_visibility()}\n
        ''')


def project_members():
    """
    Projektiryhmän jäsenten valitsin.
    """
    members = cl.make_team_member_selector(st.session_state[proj_data].get_assignees())
    return members


def closed_issues_by_milestone(members):
    """
    Palkkikaavio suljetuista issueista jäsenittäin ja milestoneittain.

    Args:
        members (list): Lista projektiryhmän jäsenten nimistä.
    """
    if len(members):
        data, x_field, y_field, color_field = st.session_state[proj_data].get_closed_issues_by_milestone(members)
        st.bar_chart(data, x=x_field, y=y_field, color=color_field, horizontal=True)


def commits_by_milestone(members):
    """
    Palkkikaavio commiteista jäsenittäin ja milestoneittain.

    Args:
        members (list): Lista projektiryhmän jäsenten nimistä.
    """
    if len(members):
        data, x_field, y_field, color_field = st.session_state[proj_data].get_commits_by_milestone(members)
        st.bar_chart(data, x=x_field, y=y_field, color=color_field, horizontal=True)


def work_hours_data(members):
    """
    Palkkikaavio työtunneista jäsenittäin ja milestoneittain.

    Args:
        members (list): Lista projektiryhmän jäsenten nimistä.
    """
    if 'sprint_hours_df_grouped' in st.session_state:
        sprint_hours_df_grouped = st.session_state['sprint_hours_df_grouped']
        if not sprint_hours_df_grouped.empty:
            try:
                filtered_df = sprint_hours_df_grouped[sprint_hours_df_grouped['user'].isin(members)]
                if not filtered_df.empty:
                    pivot_df = filtered_df.pivot(index='milestone', columns='user', values='total_hours').fillna(0)
                    st.bar_chart(pivot_df, use_container_width=True, horizontal=True)
                else:
                    st.warning("Ei löytynyt työtunteja valituille jäsenille.")
            except KeyError as e:
                st.error(f"Data puuttuu odotetuista sarakkeista: {e}")
        else:
            st.warning("Ei löytynyt työtunteja sprinteiltä.")
    else:
        st.warning("Sprinttien työtunnit eivät ole saatavilla. Varmista, että tiedot on haettu onnistuneesti start.py-sivulla.")


def milestone_selector():
    """
    Tarkasteltavien milestonejen valintakomponentti.
    """
    start_date = None
    end_date = None
    milestone_df = st.session_state[proj_data].get_milestone_data_for_slider(start_txt, end_txt)

    if len(milestone_df):
        # Koodataan milestonejen nimiin alku ja loppu -tekstit
        slider_options = milestone_df.iloc[:,0].tolist()
        slider_options = [s + ' ' + start_txt for s in slider_options] + [slider_options[-1] + ' ' + end_txt]
        start, end = st.select_slider(time_period, options=slider_options, value = (slider_options[0], slider_options[-1]), help=slider_help)

        if start and end and start != end:

            # Selvitetään koodatuista ajankohtien nimistä päivämäärät
            start_milestone, separator, start_col = start.rpartition(' ')
            end_milestone, separator, end_col = end.rpartition(' ')

            start_date = milestone_df[milestone_df.iloc[:, 0] == start_milestone].iloc[0, milestone_df.columns.get_loc(start_col)]

            if end_col == end_txt:
                end_date = milestone_df[milestone_df.iloc[:, 0] == end_milestone].iloc[0, milestone_df.columns.get_loc(end_col)]
            else:
                row_index = max(0,  milestone_df[milestone_df.iloc[:, 0] == end_milestone].index[0] - 1)
                end_date = milestone_df.iloc[row_index, milestone_df.columns.get_loc(end_txt)]

    return start_date, end_date


def closed_issues_by_date(members, start_date, end_date):
    """
    Suljetut issuet aikasarjana valittujen jäsenten ja milestonejen mukaan.

    Args:
        members (list): Lista projektiryhmän jäsenten nimistä.
        start_date (date): Aikajakson alkupvm.
        end_date (date): Aikajakson loppupvm.
    """
    if len(members):
        st.write("")
        data1, x_label1, y_label1 = st.session_state[proj_data].get_closed_issues_by_date(members, start_date, end_date)
        st.bar_chart(data1, x_label=x_label1, y_label=y_label1)


def commits_by_date(members, start_date, end_date):
    """
    Commitit aikasarjana valittujen jäsenten ja milestonejen mukaan.

    Args:
        members (list): Lista projektiryhmän jäsenten nimistä.
        start_date (date): Aikajakson alkupvm.
        end_date (date): Aikajakson loppupvm.
    """
    if len(members):
        st.write("")
        data2, x_label2, y_label2 = st.session_state[proj_data].get_commits_by_date(members, start_date, end_date)
        st.bar_chart(data2, x_label=x_label2, y_label=y_label2)


def project_page():
    """
    Moduulin pääkoodilohko, joka koostaa projektin tiedot -sivun eri komponenteista.
    """
    col1, col2, col3 = st.columns([3, 0.5, 9])

    with col1:
        # Donitsit
        st.markdown(f'#### {completion_status}')
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            milestone_donut()
        with col1_2:
            issues_donut()

    with col1:
        # Mittarit
        st.write("")
        st.markdown(f'#### {project_metrics}')
        st.write("")
        col1_1, col1_2 = col1.columns([1, 1])
        with col1_1:
            # Milestonet
            milestone_metric()
            st.write("")

            # Avoimet merge requestit
            merge_request_metric()
            st.write("")

            # Branchit
            branch_metric()

        with col1_2:
            # Issuet
            issues_metric()
            st.write("")

            # Avoimet issuet
            open_issues_metric()
            st.write("")

            # Työtunnit
            work_hours_metric()

        # Expanderit
        st.write("")
        st.write("")
        project_description_expander()
        project_info_expander()

    with col3:
        # Projektiryhmä
        members = project_members()

        # Välilehdet milestonekaavioihin
        tabs = [closed_issues, commits]
        if cl.clockify_available():
            tabs.append(work_hours)

        tab_objects_b = st.tabs(tabs)
        tab_b1, tab_b2 = tab_objects_b[:2]

        tab_b3 = None
        if cl.clockify_available():
            tab_b3 = tab_objects_b[2]

        # Suljetut issuet ja commitit milestoneittain
        with tab_b1:
            closed_issues_by_milestone(members)
        with tab_b2:
            commits_by_milestone(members)
        if tab_b3:
            with tab_b3:
                work_hours_data(members)

        # Aikajakson valinta
        start_date, end_date = milestone_selector()

        # Välilehdet aikasarjakaavioihin
        tab_objects_l = st.tabs(tabs)
        tab_l1, tab_l2 = tab_objects_l[:2]
        if cl.clockify_available():
            tab_l3 = tab_objects_l[2]

        # Aikasarjat suljetuista issueista ja commiteista
        with tab_l1:
            closed_issues_by_date(members, start_date, end_date)
        with tab_l2:
            commits_by_date(members, start_date, end_date)

        # Aikasarjat Clockify työtunneille
        if cl.clockify_available():
            with tab_l3:
                pass


if not st.session_state[proj_data]:
    cl.make_page_title(project_title)
    cl.make_start_page_button()
else:
    avatar = st.session_state[proj_data].get_avatar()
    cl.make_page_title(st.session_state[proj_data].get_name(), avatar)
    project_page()