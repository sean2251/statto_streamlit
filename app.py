import streamlit as st
import pandas as pd

from utils.load_data import load_team_csvs, load_tournament_csvs

from views.points import show_points
from views.possessions import show_possessions
from views.passes import show_passes
from views.player_stats import show_player_stats


DATA_DIR = 'data'
SUBVIEWS = ["Passes", "Points", "Possessions", "Player Stats", "Defensive Blocks"]


# Load data
team_data = load_team_csvs(DATA_DIR)
tournament_data = load_tournament_csvs(DATA_DIR)
tournaments = list(tournament_data.keys())

st.set_page_config(layout="wide")

# --- Simple Login ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# if not st.session_state.logged_in:
#     st.title('Login Required')
#     username = st.text_input('Username')
#     password = st.text_input('Password', type='password')
#     login_btn = st.button('Login')
#     if login_btn:
#         if username == st.secrets.username and password == st.secrets.password:
#             st.session_state.logged_in = True
#             st.success('Login successful!')
#             st.rerun()
#         else:
#             st.error('Invalid username or password.')
#     st.stop()

# Sidebar for data selection
data_type = st.sidebar.radio('View', ['Tournaments', 'Team Data'])

# Display data based on selection
st.header(data_type)
if data_type == 'Team Data':
    for fname, data in team_data.items():
        st.subheader(fname)
        st.dataframe(data)
elif data_type == 'Tournaments':
    # Create subview data based on selected tournaments and games
    subview_data = dict.fromkeys(SUBVIEWS)
    selected_tournaments = st.sidebar.multiselect('Tournaments', tournaments, default=tournaments)
    for tournament in selected_tournaments:
        games = list(tournament_data[tournament].keys())
        selected_games = st.sidebar.multiselect(tournament, games, default=games)
        for game in selected_games:
            for subview_name in SUBVIEWS:
                old_subview_data = subview_data[subview_name]
                new_subview_data = tournament_data[tournament][game][subview_name]
                subview_data[subview_name] = pd.concat([old_subview_data, new_subview_data])

    # Display selected subview
    subview = st.sidebar.radio("Subview", SUBVIEWS[:-1])
    if subview == "Passes":
        df = subview_data[subview]
        show_passes(df)
    elif subview == "Points":
        df = subview_data[subview]
        show_points(df)
    elif subview == "Possessions":
        df = subview_data[subview]
        passes_df = subview_data["Passes"]
        if passes_df is not None:
            show_possessions(passes_df)
        else:
            st.info("No passes data available for selected games")
    elif subview == "Player Stats":
        pass_df = subview_data["Passes"]
        df = subview_data["Player Stats"]
        show_player_stats(pass_df, df)

    show_data = st.checkbox('View All Data', value=False)
    if show_data:
        st.dataframe(df)