import streamlit as st
import pandas as pd
import altair as alt
import requests
import os


# Kielikäännökset
members = "Projektiryhmän jäsenet"
help_project_member = "Projektiryhmän jäsen on projektin member, jolle on assignattu issueita tai joka on tehnyt committeja."
specify_proj = "Määritä GitLab-projekti"
info_specify_proj = "Anna ensin tarkasteltavan projektin GitLab-osoite!"


def make_page_title(title):
    """
    Sivun otsikko alleviivauksella
    """
    # Otsikko
    st.markdown(
        f'<h2 style="margin-top: 0px; margin-bottom: 5px; padding-top: 0px; color: #FAEBC8">{title}</h2>',
        unsafe_allow_html=True
    )
    # Viiva
    st.markdown(
        "<hr style='margin-top: 0px; margin-bottom: 0px; border: 1px solid #F49E25;'>",
        unsafe_allow_html=True
    )


def make_start_page_button():
    """
    Kehoite ja painike projektin valintaan
    """
    st.info(info_specify_proj, icon="ℹ️")
    if st.button(specify_proj):
        st.switch_page('app_pages/start.py')


def make_donut(input_response, input_text, input_color):
    """
    Donitsikaavio
    Koodin lähde: https://github.com/dataprofessor/population-dashboard/blob/master/streamlit_app.py
    """
    if input_color == 'blue':
        chart_color = ['#29b5e8', '#155F7A']
    if input_color == 'green':
        chart_color = ['#27AE60', '#12783D']
    if input_color == 'orange':
        chart_color = ['#F49E25', '#FAEBC8'] # RepoRousku
    if input_color == 'red':
        chart_color = ['#E74C3C', '#781F16']
        
    source = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100-input_response, input_response]
    })
    source_bg = pd.DataFrame({
        "Topic": ['', input_text],
        "% value": [100, 0]
    })
        
    plot = alt.Chart(source).mark_arc(innerRadius=45, cornerRadius=25).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            #domain=['A', 'B'],
                            domain=[input_text, ''],
                            # range=['#29b5e8', '#155F7A']),  # 31333F
                            range=chart_color),
                        legend=None),
    ).properties(width=130, height=130)
        
    text = plot.mark_text(align='center', color="#29b5e8", font="Lato", fontSize=32, fontWeight=700, fontStyle="italic").encode(text=alt.value(f'{input_response} %'))
    plot_bg = alt.Chart(source_bg).mark_arc(innerRadius=45, cornerRadius=20).encode(
        theta="% value",
        color= alt.Color("Topic:N",
                        scale=alt.Scale(
                            # domain=['A', 'B'],
                            domain=[input_text, ''],
                            range=chart_color),  # 31333F
                        legend=None),
    ).properties(width=130, height=130)
    return plot_bg + plot + text


def make_team_member_selector(member_list):
    """
    Projektiryhmän jäsenten listaus ja valinta tarkasteluun
    """

    st.markdown(
        '''
        <style>
        .css-1lcbmhc { margin-top: -16px; }
        </style>
        ''',
        unsafe_allow_html=True
    )

    selected = st.multiselect(
        members,
        member_list,
        member_list,
        help = help_project_member)

    return selected


def validate_url(url):
    """
    Tarkastaa, onko annettu url validi
    """
    if not url.startswith("https://") or url == "https://":
        return False

    try:
        response = requests.get(url)
        try:
            response.raise_for_status()
            return True
        except requests.exceptions.HTTPError:
            return False
    except requests.exceptions.ConnectionError:
        return False


def clockify_available():
    """
    Palauttaa True, jos Clockifyn tiedot saatavilla
    TODO: Toteuta funktio
    """
    return False


def in_docker():
    """
    Palauttaa True, jos ohjelmaa ajetaan Docker-kontissa
    """
    return os.path.exists("/.dockerenv")