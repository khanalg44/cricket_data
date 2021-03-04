#!/usr/bin/env python3

import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

from get_profile import get_player_profile
from find_name import find_name


st.set_page_config(
    page_title="Ex-stream-ly Cool App",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded" )


st.title("Welcome to Cric-Data!")#, color='red')
st.sidebar.title('Find Player Profile')

user_input_player = st.sidebar.text_input(label="Enter Player Name")#, value="SR Tendulkar")

if user_input_player:

    player_name = find_name(user_input_player)
    
    if player_name is None:
        st.markdown(user_input_player+" is not found.")
    else:
        bat_bowl = st.sidebar.selectbox(label="Batting/Bowling Profile",
                                        options=("bat",
                                                "bowl"))
    
        year_from = st.sidebar.number_input("Year from", min_value=2008, max_value=2021, value = 2008, step=1)
        year_to =   st.sidebar.number_input("Year to", min_value=2008, max_value=2021, value = 2021, step=1)
        if year_to < year_from:
            year_to = year_from
    
        bat = True
        if bat_bowl=='bowl':
            bat = False
        
        show_plot = st.sidebar.checkbox(label="Show Plot", value=False)
    
        #player_name = st.text_input("Player Name","SR Tendulkar")
        #bat = st.checkbox("Bat")
        #bowl = st.checkbox("Bowl")
        print (player_name)
        if player_name:
            st.markdown('**'+player_name+'**')
            df = get_player_profile(player_name, batsman=bat,
            year_from=year_from, year_to=year_to)
            st.table(df)
            if show_plot:
                fig = px.bar(df, x='season', y='Runs')
                st.plotly_chart(fig)
                st.text("More plots to appear shortly.")
    

st.sidebar.title('Team Profile')

team_name = st.sidebar.selectbox(label="Team name", 
                                options=("Chennai Super Kings",
                                         "Delhi Capitals",
                                        "Punjab Kings",
                                        "Kolkata Knight Riders",
                                        "Mumbai Indians",
                                        "Rajasthan Royals",
                                        "Royal Challengers Bangalore",
                                        "Sunrisers Hyderabad") )
