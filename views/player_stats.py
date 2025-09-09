import streamlit as st
import pandas as pd

def show_player_stats(passes_df, player_stats_df, defensive_blocks_df):

    # df = df.drop(columns=[
    #     "Points played", 
    #     "Average completed throw distance (m)",
    #     "Average completed throw gain (m)",
    #     "Average caught pass distance (m)",
    #     "Average caught pass gain (m)"
    #     ], axis=1)
    # df = df.groupby("Player").sum().reset_index()
    # df["Throwing Percentage"]
    st.write("Player stats view is under construction.")

    st.text("### Passes")
    st.dataframe(passes_df)
    st.text("### Player Stats")
    st.dataframe(player_stats_df)
    st.text("### Defensive Blocks")
    st.dataframe(defensive_blocks_df)
   

 
 # Points played / involvement
    # Total points played
    # O points played
    # O points won
    # D points played
    # D points won
    # Touches
    # Turnovers (includes throwing errors and receiver errors)
    # Points played with touches
    # Defensive blocks
    # Points played with defensive blocks where other team had possesion

# Thrower Stats
    # Throws
    # Assists (A1)
    # Secondary assists (A2)
    # Possessions initiated (Pick up)
    # Throwing errors
    # Total completed throw distance (m)
    # Total completed throw gain (m)
    # Average completed throw distance (m)
    # Average completed throw gain (m)
    # Overall throw completion percentage
    # Huck completion percentage
    # Short throw completion percentage
    # Completion percentage from center of field
    # Completion percentage from near sidelines

# Receiver Stats
    # Catches
    # Goals
    # Receiver errors (drops)

    # Defensive blocks

    # Total caught pass distance (m)
    # Total caught pass gain (m)
    # Average caught pass distance (m)
    # Average caught pass gain (m)
