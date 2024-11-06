import streamlit as st
import libraries.components as cl

# Kielikäännökset
member_title = "Jäsenet"

def member_page():
    """
    Sivu projektiryhmän jäseten statistiikan tarkateluun
    """
    cl.make_page_title(member_title)

    cl.make_team_member_selector(["Aku Ankka","Hessu Hopo","Minni Hiiri"])

member_page()