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
            df = st.session_state[proj_data].get_issues()

            # Assigneet omille riveilleen
            df_exploded = df.explode('assignees')

            # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
            df_filtered = df_exploded[df_exploded['assignees'].isin(members)]

            # Lasketaan issueiden määrä kullekin milestone ja assignees -yhdistelmälle
            grouped_data = df_filtered.groupby(['milestone', 'assignees']).size().reset_index(name='kpl')

        elif option_bar == commits:
            df_commits = st.session_state[proj_data].get_commits()
            df_milestones = st.session_state[proj_data].get_milestones()

            # Liitetään milestone commit-päivämäärän perusteella
            def get_milestone_for_commit(commit_date):
                milestone = df_milestones[(df_milestones["start_date"] <= commit_date) & (df_milestones["due_date"] >= commit_date)]
                return milestone["title"].iloc[0] if not milestone.empty else None

            # Lisätään milestone-tieto commits_df:ään
            df_commits["milestone"] = df_commits["committed_date"].apply(get_milestone_for_commit)

            # Suodatetaan pois commitit, joille ei löytynyt milestonea
            df_commits = df_commits.dropna(subset=["milestone"])

            # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
            df_commits = df_commits[df_commits['author_name'].isin(members)]

            # Lasketaan commit-määrät per milestone ja author
            grouped_data = df_commits.groupby(["milestone", "author_name"]).size().reset_index(name="kpl")

            # Varmistetaan, että data on oikeassa muodossa kaaviota varten
            grouped_data.columns = ["milestone", "assignees", "kpl"]

        else: # work_hours
            # TODO: Clockify-tunnit
            import random
            grouped_data = {
                "milestones": ['Sprint 1'] * 5 + ['Sprint 2'] * 5 + ['Sprint 3'] * 5 + ['Sprint 4'] * 5 + ['Sprint 5'] * 5 + ['Sprint 6'] * 5,
                "member": ['Aku', 'Hessu', 'Minni'] * 10,
                "kpl": [random.randint(20, 100) for _ in range(30)],
            }

        grouped_data['kpl'] = grouped_data['kpl'].astype(int)
        st.bar_chart(grouped_data, x="milestone", y="kpl", color="assignees", horizontal=True)

        # Viivakaavio

        # Datatyypin valinta viivakaavioon
        col3_1, col3_2 = col3.columns([1, 5])
        with col3_1:
            option_line = st.selectbox(" ",options, label_visibility="hidden", key="datatype2", index=1)

        if option_line == closed_issues:
            df = st.session_state[proj_data].get_closed_issues()

            # Assigneet omille riveilleen
            df_exploded = df.explode('assignees')

            # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
            df_exploded = df_exploded[df_exploded['assignees'].isin(members)]

            grouped_data = df_exploded.groupby(['closed_at', 'assignees']).size().reset_index(name='value')

            st.line_chart(grouped_data, x="closed_at", y="value", color="assignees")

        elif option_line == commits:
            df = st.session_state[proj_data].get_commits()

            # Suodatetaan assigneet selectorissa tehdyn valinnan mukaan
            df = df[df['author_name'].isin(members)]

            # Lasketaan commits per päivämäärä ja author_name
            grouped_data = df.groupby(['committed_date', 'author_name']).size().reset_index(name='value')
            grouped_data['value'] = grouped_data['value'].astype(int)

            st.line_chart(grouped_data, x="committed_date", y="value", color="author_name")

        else: # work_hours
            # TODO: Clockify-tunnit
            from datetime import datetime, timedelta
            import random
            grouped_data = {
                "committed_date": [datetime.today() + timedelta(days=i) for i in range(30)],
                "author_name": ['Aku', 'Hessu', 'Minni'] * 10,
                "value": [random.randint(20, 100) for _ in range(30)],
            }

            st.line_chart(grouped_data, x="committed_date", y="value", color="author_name")


if not st.session_state[proj_data]:
    cl.make_page_title(project_title)
    cl.make_start_page_button()
else:
    cl.make_page_title(st.session_state[proj_data].get_name())
    project_page()