import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.draw import draw_field, norm_to_field_x, norm_to_field_y, show_custom_legend


def show_possessions(df):
    col_select, col_chart, col_legend = st.columns([1, 2, 2])

    # Left column - Selection interface
    with col_select:
        # Game selection
        games = df['tournament_game'].unique()
        selected_game = st.selectbox('Select Game', games)

        # Create container for scrollable area
        with st.container(height=800):

            # Filter for selected game
            game_df = df[df['tournament_game'] == selected_game]

            points = sorted(game_df['Point'].unique())
            point_possessions = {}
            selected_possessions = []

            # Add buttons for quick selection
            if st.button("Unselect all"):
                for key in st.session_state.keys():
                    if key.startswith("p"):
                        st.session_state[key] = False

            if st.button("Select all D possessions"):
                for point in points:
                    point_df = game_df[game_df['Point'] == point]
                    started_on_offense = point_df['Started on offense?'].iloc[0]
                    if not started_on_offense:  # D possessions
                        possessions = sorted(point_df['Possession'].unique())
                        for possession in possessions:
                            st.session_state[f"p{point}_pos{possession}"] = True

            if st.button("Select all O possessions"):
                for point in points:
                    point_df = game_df[game_df['Point'] == point]
                    started_on_offense = point_df['Started on offense?'].iloc[0]
                    if started_on_offense:  # O possessions
                        possessions = sorted(point_df['Possession'].unique())
                        for possession in possessions:
                            st.session_state[f"p{point}_pos{possession}"] = True


            # Create dictionary of point -> possessions and selection interface
            for point in points:
                point_df = game_df[game_df['Point'] == point]
                possessions = sorted(point_df['Possession'].unique())
                point_possessions[point] = possessions

                # Get whether this was an O-point or D-point
                started_on_offense = point_df['Started on offense?'].iloc[0]
                point_type = "O" if started_on_offense else "D"
                
                # Point header with O/D indicator
                st.write(f"Point {point} ({point_type})")

                # Simple indented possessions
                for possession in point_possessions[point]:
                    possession_selected = st.checkbox(
                        f"  Possession {possession}",
                        key=f"p{point}_pos{possession}"
                    )
                    if possession_selected:
                        selected_possessions.append((point, possession))
                

    # Middle column - Main plot
    with col_chart:
        fig = draw_field()

        if selected_possessions:
            filtered_df = pd.DataFrame()  # Create empty DataFrame
            for point, possession in selected_possessions:
                point_pos_df = game_df[
                    (game_df['Point'] == point) & 
                    (game_df['Possession'] == possession)
                ]
                filtered_df = pd.concat([filtered_df, point_pos_df])
        else:
            filtered_df = game_df

        # Draw passes similar to show_passes()
        for idx, row in filtered_df.iterrows():
            sx = norm_to_field_x(row['Start X (0 -> 1 = left sideline -> right sideline)'])
            sy = norm_to_field_y(row['Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
            ex = norm_to_field_x(row['End X (0 -> 1 = left sideline -> right sideline)'])
            ey = norm_to_field_y(row['End Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
            turnover = row['Turnover?']
            thrower_error = row['Thrower error?']
            receiver_error = row['Receiver error?']

            # Default: completed pass
            start_marker = dict(symbol="square", color="green", size=10)
            end_marker = dict(symbol="circle", color="green", size=12)
            line_color = "green"
            show_end_marker = True

            # Throwaway: turnover + thrower error
            if turnover == 1 and thrower_error == 1:
                start_marker = dict(symbol="square", color="red", size=16)
                line_color = "red"
                show_end_marker = False

            # Drop: turnover + receiver error
            elif turnover == 1 and receiver_error == 1:
                start_marker = dict(symbol="square", color="green", size=10)
                end_marker = dict(symbol="circle", color="red", size=16)
                line_color = "red"
                show_end_marker = True

            # Draw the line
            fig.add_trace(go.Scatter(
                x=[sx, ex],
                y=[sy, ey],
                mode="lines",
                line=dict(color=line_color, width=2),
                hoverinfo="skip",
                showlegend=False
            ))

            # Draw start marker
            fig.add_trace(go.Scatter(
                x=[sx],
                y=[sy],
                mode="markers",
                marker=dict(
                    color=[start_marker["color"]],
                    symbol=[start_marker["symbol"]],
                    size=[start_marker["size"]],
                    line=dict(width=1, color="black")
                ),
                text=[f"Thrower: {row['Thrower']}<br>Receiver: {row['Receiver']}<br>Point: {row['Point']}<br>Possession: {row['Possession']}"],
                hoverinfo="text",
                showlegend=False
            ))

            # Draw end marker if needed
            if show_end_marker:
                fig.add_trace(go.Scatter(
                    x=[ex],
                    y=[ey],
                    mode="markers",
                    marker=dict(
                        color=[end_marker["color"]],
                        symbol=[end_marker["symbol"]],
                        size=[end_marker["size"]],
                        line=dict(width=1, color="black")
                    ),
                    text=[f"Thrower: {row['Thrower']}<br>Receiver: {row['Receiver']}<br>Point: {row['Point']}<br>Possession: {row['Possession']}"],
                    hoverinfo="text",
                    showlegend=False
                ))

        st.plotly_chart(fig, use_container_width=False)

    # Right column - Legend
    with col_legend:
        st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
        show_custom_legend()

    # Show filtered dataframe below
    st.dataframe(filtered_df)