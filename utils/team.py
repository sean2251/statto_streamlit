import os
import pandas as pd
from collections import defaultdict
import streamlit as st


DATA_DIR = 'data'
SUBVIEWS = ["Passes", "Points", "Defensive Blocks", "Stall Outs Against", "Player Stats", "Possessions"]

# Utility to load top-level CSVs
def load_team_csvs(data_dir):
    team_data = {}
    for data_file in os.listdir(data_dir):
        data_path = os.path.join(data_dir, data_file)
        if os.path.isfile(data_path) and data_file.endswith('.csv'):
            team_data[data_file] = pd.read_csv(data_path)
    return team_data

# Rename stat file keys for display simplicity
def rename_stat_files(data):
    for tournament in data:
        for game in data[tournament]:
            keys_to_rename = []
            for old_key in list(data[tournament][game].keys()):
                new_key = old_key.split(' vs.')[0]
                data[tournament][game][new_key] = data[tournament][game].pop(old_key)

# Utility to recursively load all CSVs in all tournament folders under data/
def load_tournament_csvs(data_dir):
    tournament_data = defaultdict(lambda: defaultdict(dict))
    for tournament_folder in os.listdir(data_dir):
        tournament_path = os.path.join(data_dir, tournament_folder)
        if os.path.isdir(tournament_path):
            for game_folder in os.listdir(tournament_path):
                game_path = os.path.join(tournament_path, game_folder)
                if os.path.isdir(game_path):
                    for file in os.listdir(game_path):
                        if file.endswith('.csv'):
                            file_path = os.path.join(game_path, file)
                            try:
                                df = pd.read_csv(file_path)
                                # If this is a Passes file, add the "tournament / game" column
                                if file.lower().startswith("passes"):
                                    tournament_game_str = f"{tournament_folder}_{game_folder}"
                                    df["tournament_game"] = tournament_game_str
                                tournament_data[tournament_folder][game_folder][file] = df
                            except Exception as e:
                                st.warning(f'Could not load {file_path}: {e}')
    rename_stat_files(tournament_data)
    return tournament_data