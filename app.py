import streamlit as st
import pandas as pd
import os
from collections import defaultdict

from utils.team import load_team_csvs, load_tournament_csvs, SUBVIEWS, DATA_DIR
from utils.draw import show_passes, show_blocks, show_endzone_attempts, draw_field
from utils.stats import show_points


# Load data
team_data = load_team_csvs(DATA_DIR)
tournament_data = load_tournament_csvs(DATA_DIR)
tournaments = list(tournament_data.keys())

# Sidebar for data selection
data_type = st.sidebar.radio('View', ['Team Data', 'Tournaments'])


# Display data based on selection
st.header(data_type)
if data_type == 'Team Data':
    url = "https://docs.google.com/spreadsheets/d/1rS-ZR8lRUILphhovvB744qNi7PODkLiG_hcyg5PE0vc/edit?gid=0#gid=0"
    st.write(f"[Teamwide Summary Stats]({url})")
    for fname, data in team_data.items():
        st.subheader(fname)
        st.dataframe(data)
elif data_type == 'Tournaments':
    # Create subview data based on selected tournaments and games
    subview_data = dict.fromkeys(SUBVIEWS)
    selected_tournaments = st.sidebar.multiselect('Tournaments', tournaments, default=tournaments)
    for tournament in selected_tournaments:
        games = list(tournament_data[tournament].keys())
        selected_games = st.sidebar.multiselect('Games', games, default=games)
        for game in selected_games:
            for subview_name in SUBVIEWS:
                old_subview_data = subview_data[subview_name]
                new_subview_data = tournament_data[tournament][game][subview_name]
                subview_data[subview_name] = pd.concat([old_subview_data, new_subview_data])

    # Display selected subview
    subview = st.sidebar.radio("Subview", SUBVIEWS)
    df = subview_data[subview]

    if df is not None:
        if subview == "Passes":
            passes_view = st.radio('', ['All Passes', 'Endzone Attempts'])
            if passes_view == 'All Passes':
                show_passes(df)
            elif passes_view == 'Endzone Attempts':
                show_endzone_attempts(df)
        elif subview == "Points":
            show_points(df)
        elif subview == "Defensive Blocks":
            show_blocks(df)
        elif subview == "Stall Outs Against":
            st.info("No visualizations available for this subview")
        elif subview == "Player Stats":
            st.info("No visualizations available for this subview")
        elif subview == "Possessions":
            st.info("No visualizations available for this subview")

        show_data = st.checkbox('View All Data', value=True)
        if show_data:
            st.dataframe(df)
    else:
         st.info("Select at least one game to view data")
