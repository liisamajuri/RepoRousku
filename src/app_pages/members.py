import streamlit as st
import libraries.components as cl

# Kielikäännökset
member_title = "Jäsenet"

# Muuttujat
proj_data = "proj_data"

def member_page():
    """
    Sivu projektiryhmän jäseten statistiikan tarkasteluun
    """
    cl.make_team_member_selector(st.session_state[proj_data].get_assignees())


cl.make_page_title(member_title)

if not st.session_state[proj_data]:
    cl.make_start_page_button()
else:
    member_page()
