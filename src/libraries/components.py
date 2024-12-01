"""
RepoRouskun komponenttikirjasto, joka sisältää sovelluksen eri sivuilla yhteisesti käytettävät komponentit ja toiminnallisuudet.
"""

import streamlit as st
import pandas as pd
import altair as alt
import requests
from datetime import datetime
from tzlocal import get_localzone

from streamlit_theme import st_theme


# Kielikäännökset
members = "Projektiryhmä"
help_project_member = "Projektiryhmän jäsen on projektin member, jolle on assignattu issueita tai joka on tehnyt committeja."
specify_proj = "Määritä GitLab-projekti"
info_specify_proj = "Anna ensin tarkasteltavan projektin GitLab-osoite!"

light_primary_color = "#2C9FD8" # Curious Blue
dark_primary_color = "#126C96" # Matisse
dark_background = "#0e1117"
white_color = "#FFFFFF"
red_color = "#FF4B4B"


def get_background_color():
    """
    Palauttaa aktiivisen taustavärin.

    Returns:
        (str): Taustaväri.
    """
    theme = st_theme()
    return theme['backgroundColor'].lower() if theme else None


def get_title_color():
    """
    Palauttaa otsikon värin valitun väriteeman mukaan.
    Ei kannata käyttää, koska hakemisessa on viivettä.

    Returns:
        (str): Otsikon väri taustavärin mukaan.
    """
    bc = get_background_color()
    if bc and bc.lower() == dark_background:
        return white_color
    return light_primary_color


def make_page_title(title, avatar_url=None):
    """
    Sivun otsikko alleviivauksella ja mahdollisella avattarella.

    Args:
        avatar_url (str, optional): Projektin avattaren url.
    """
    # Otsikko avattarella, jos kuva määritelty ja oikeudet riittävät sen saamiseen
    if avatar_url and requests.get(avatar_url).status_code == 200:
        st.markdown(
            f'<div style="display: flex; align-items: center;">'
            f'<img src="{avatar_url}" width="50" style="margin-right: 10px;">'
            f'<h2 style="color: {light_primary_color}; margin-top: 0px; margin-bottom: 5px;">{title}</h2>'
            f'</div>',
            unsafe_allow_html=True
        )
    # Pelkkä otsikko
    else:
        st.markdown(
            f'<h2 style="color: {light_primary_color}; margin-top: 0px; margin-bottom: 5px;">{title}</h2>',
            unsafe_allow_html=True
        )

    # Viiva otsikon alapuolelle
    st.markdown(
        f"<hr style='margin-top: 0px; margin-bottom: 0px; border: 1px solid {red_color};'>",
        unsafe_allow_html=True
    )


def make_start_page_button():
    """
    Kehoite ja painike projektin valintaan.
    """
    st.info(info_specify_proj, icon="ℹ️")
    if st.button(specify_proj):
        st.switch_page('app_pages/start.py')


def make_donut(input_response, input_text, input_color):
    """
    Donitsikaavio annettujen parametrien mukaisesti.
    Koodin lähde: https://github.com/dataprofessor/population-dashboard/blob/master/streamlit_app.py

    Args:
        input_response (int): Arvo.
        input_text (str): Teksti.
        input_color (str): Väriteema.
    """
    if input_color == 'blue':
        chart_color = [light_primary_color, dark_primary_color] # RepoRousku
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
    Projektiryhmän jäsenten listaus ja valinta tarkasteluun.

    Args:
        member_list (list): Lista jäsenten nimistä.
    """
    st.markdown(
        '''
        <style>
        .css-1lcbmhc { margin-top: -16px; }
        </style>
        ''',
        unsafe_allow_html=True
    )

    selected = st.pills(
        members,
        sorted(member_list),
        selection_mode = 'multi',
        default = member_list,
        help = help_project_member)

    return selected


def validate_url(url):
    """
    Tarkastaa, onko annettu url validi.

    Args:
        url (str): Tarkastettava url.
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
    Palauttaa True, jos Clockifyn tiedot ja työtunnit saatavilla.

    Returns:
        (bool): True, jos Clockifyn data käytettävissä.
    """
    return (st.session_state.get("clockify_workspace") is not None and 
            st.session_state.get("clockify_project") is not None and 
            'clockify_data' in st.session_state and not st.session_state['clockify_data'].empty)


def convert_timestamp_to_local_date(iso_date):
    """
    Muuttaa ISO 8601 aikaleiman paikallisen aikavyöhykkeen datetime.date formaattia olevaksi päivämääräksi

    Args:
        iso_date (timestamp): Aikaleima ISO 8601 formaatissa

    Returns:
        (datetime.date): Päivämäärä vvvv-kk-pp

    """
    if iso_date:
        # Muunnetaan aikaleima UTC-ajaksi
        utc_time = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))

        # Selvitetään paikallinen aikavyöhyke
        local_timezone = get_localzone()

        # Muunnetaan utc-aikaleima paikalliseen aikaan
        local_time = utc_time.astimezone(local_timezone)

        # Palauta pelkkä päivämäärä
        return local_time.date()


def format_time_columns(df, column_list):
    """
    Muuttaa parametrina annettujen aikaleimasarakkeiden ajan lokaaliksi ja 
    formaatttiin ISO 8601 -> datetime.date.

    Args:
        df (DataFrame): Dataframe, jossa formatoitavat sarakkeet.
        column_list (list): Lista sarakenimistä.

    Returns:
        (DataFrame): DataFrame, jossa määritellyt sarakkeet formatoitu.
    """
    for column in column_list:
        # Muutetaan aikaleima datetime-objektiksi ja poistetaan aikavyöhyke
        df[column] = df[column].apply(convert_timestamp_to_local_date)

    return df