import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.colors


FIELD_LENGTH = 110  # total length (including both endzones)
FIELD_WIDTH = 40    # width (sideline to sideline)
ENDZONE_DEPTH = 20  # each endzone

def show_custom_legend():
    legend_fig = go.Figure()

    # Pass: blue square + blue line + blue circle
    legend_fig.add_trace(go.Scatter(
        x=[0, 1], y=[3, 3],
        mode="lines",
        line=dict(color="green", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))
    legend_fig.add_trace(go.Scatter(
        x=[0], y=[3],
        mode="markers",
        marker=dict(symbol="square", color="green", size=16, line=dict(width=1, color="black")),
        showlegend=False,
        hoverinfo="skip"
    ))
    legend_fig.add_trace(go.Scatter(
        x=[1], y=[3],
        mode="markers",
        marker=dict(symbol="circle", color="green", size=18, line=dict(width=1, color="black")),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Drop: blue square + red line + red circle
    legend_fig.add_trace(go.Scatter(
        x=[0, 1], y=[2, 2],
        mode="lines",
        line=dict(color="red", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))
    legend_fig.add_trace(go.Scatter(
        x=[0], y=[2],
        mode="markers",
        marker=dict(symbol="square", color="green", size=16, line=dict(width=1, color="black")),
        showlegend=False,
        hoverinfo="skip"
    ))
    legend_fig.add_trace(go.Scatter(
        x=[1], y=[2],
        mode="markers",
        marker=dict(symbol="circle", color="red", size=20, line=dict(width=1, color="black")),
        showlegend=False,
        hoverinfo="skip"
    ))

    # Throwaway: red square + red line (no end marker)
    legend_fig.add_trace(go.Scatter(
        x=[0, 1], y=[1, 1],
        mode="lines",
        line=dict(color="red", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))
    legend_fig.add_trace(go.Scatter(
        x=[0], y=[1],
        mode="markers",
        marker=dict(symbol="square", color="red", size=20, line=dict(width=1, color="black")),
        showlegend=False,
        hoverinfo="skip"
    ))

    legend_fig.update_layout(
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.2, 1.8]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.5, 3.5]),
        width=180,
        height=140,
        margin=dict(l=0, r=0, t=0, b=0),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Add text labels using annotations (smaller font, closer to markers)
    legend_fig.add_annotation(x=1.3, y=3, text="Pass", showarrow=False, font=dict(size=14), xanchor="left", yanchor="middle")
    legend_fig.add_annotation(x=1.3, y=2, text="Drop", showarrow=False, font=dict(size=14), xanchor="left", yanchor="middle")
    legend_fig.add_annotation(x=1.3, y=1, text="Throwaway", showarrow=False, font=dict(size=14), xanchor="left", yanchor="middle")

    st.plotly_chart(legend_fig, use_container_width=False)

def draw_field():
    # Draw the field as a rectangle
    field_shape = dict(
        type="rect",
        x0=0, y0=0,
        x1=FIELD_WIDTH, y1=FIELD_LENGTH,
        line=dict(color="green", width=3),
        fillcolor="rgba(0,255,0,0.05)",
        layer="below"
    )
    # Endzone lines (flipped: endzone1 is now at the top, endzone2 at the bottom)
    endzone1 = dict(
        type="rect",
        x0=0, y0=FIELD_LENGTH-ENDZONE_DEPTH,
        x1=FIELD_WIDTH, y1=FIELD_LENGTH,
        line=dict(color="blue", width=2, dash="dot"),
        fillcolor="rgba(0,0,255,0.05)",
        layer="below"
    )
    endzone2 = dict(
        type="rect",
        x0=0, y0=0,
        x1=FIELD_WIDTH, y1=ENDZONE_DEPTH,
        line=dict(color="blue", width=2, dash="dot"),
        fillcolor="rgba(0,0,255,0.05)",
        layer="below"
    )

    # Create figure
    fig = go.Figure()

    # Add field and endzones
    fig.update_layout(
        shapes=[field_shape, endzone1, endzone2],
        width=400,
        height=1100,  # keep aspect ratio
        xaxis=dict(range=[0, FIELD_WIDTH], showgrid=False, zeroline=False, showticklabels=True),
        yaxis=dict(range=[0, FIELD_LENGTH], showgrid=False, zeroline=False, showticklabels=True),
    )
    return fig

def norm_to_field_x(x_norm):
    # x_norm: 0 (left sideline) to 1 (right sideline)
    return x_norm * FIELD_WIDTH

def norm_to_field_y(y_norm):
    # y_norm: 0 (back of opponent endzone) to 1 (back of own endzone)
    # To flip the direction, invert the y axis: 0 (back of own endzone) to 1 (back of opponent endzone)
    return (1 - y_norm) * FIELD_LENGTH

def show_passes(df):
    col_chart, col_legend = st.columns([3, 1])
    with col_chart:
        fig = draw_field()
    
        # TODO
        # Player specific stats
        # Goals, A1, A2, Blocks
        # Touches, turnovers, thrower errors, receiver errors
        # Thrower completion percentage, Receiver completion percentage
        # Average throwing distance / yardage, average receiving distance / yardage
        # Breakdown of throws by type (short, medium, long)
        # Completion rates by type (short, medium, long)

        # Additional game filtersI
        # O points vs D points
        # Clean scores, dirty scores, broken points
        # Turnovers - distance compared to average completed throw. Rate of EZ attempts to average completed throw. # of hucks vs short throws.
    
        thrower_options = [x for x in df['Thrower'].unique() if pd.notnull(x)]
        thrower = st.selectbox('Thrower', sorted(thrower_options, key=str), index=None, placeholder='Select a thrower')
        receiver_options = [x for x in df['Receiver'].unique() if pd.notnull(x)]
        receiver = st.selectbox('Receiver', sorted(receiver_options, key=str), index=None, placeholder='Select a receiver')
        point = st.selectbox('Point', df['Point'].unique(), index=None, placeholder='Select a point')

        if thrower:
            df = df[df['Thrower'] == thrower]
        if receiver:
            df = df[df['Receiver'] == receiver]
        if point:
            df = df[df['Point'] == point]

        df = df.copy()
        df['possession_ID'] = (
            df['tournament_game'].astype(str) + "_" +
            df['Point'].astype(str) + "_" +
            df['Possession'].astype(str)
        )

        differentiate_possessions = st.checkbox("Differentiate Possessions", value=False)

        # Prepare color palette for possessions
        unique_possessions = df['possession_ID'].unique()
        num_possessions = len(unique_possessions)
        if num_possessions <= 20:
            palette = plotly.colors.qualitative.Plotly
            colors = [palette[i % len(palette)] for i in range(num_possessions)]
        else:
            colors = [f"hsl({int(360*i/num_possessions)},70%,50%)" for i in range(num_possessions)]
        possession_color_map = dict(zip(unique_possessions, colors))

        # Assign line color for each throw
        if differentiate_possessions:
            df['line_color'] = df['possession_ID'].map(possession_color_map)
        else:
            df['line_color'] = df['Turnover?'].map({0: "green", 1: "red"})

        # Batch lines by color (possession or turnover/completion)
        for idx, row in df.iterrows():
            sx = norm_to_field_x(row['Start X (0 -> 1 = left sideline -> right sideline)'])
            sy = norm_to_field_y(row['Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
            ex = norm_to_field_x(row['End X (0 -> 1 = left sideline -> right sideline)'])
            ey = norm_to_field_y(row['End Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
            color = row['line_color']
            turnover = row['Turnover?']
            thrower_error = row['Thrower error?']
            receiver_error = row['Receiver error?']

            # Default: completed pass
            start_marker = dict(symbol="square", color=color, size=10)
            end_marker = dict(symbol="circle", color=color, size=12)
            line_color = color
            show_end_marker = True

            # Throwaway: turnover + thrower error
            if turnover == 1 and thrower_error == 1:
                start_marker = dict(symbol="square", color="red", size=16)
                line_color = "red"
                show_end_marker = False  # No end marker for throwaway

            # Drop: turnover + receiver error
            elif turnover == 1 and receiver_error == 1:
                start_marker = dict(symbol="square", color=color, size=10)
                end_marker = dict(symbol="circle", color="red", size=16)
                line_color = "red"
                show_end_marker = True

            # Draw the line
            fig.add_trace(go.Scatter(
                x=[sx, ex] if show_end_marker else [sx, ex],
                y=[sy, ey] if show_end_marker else [sy, ey],
                mode="lines",
                line=dict(color=line_color, width=2),
                hoverinfo="skip",
                showlegend=False
            ))

            # Draw the start marker (always a square)
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
                text=[f"Thrower: {row['Thrower']}<br>Receiver: {row['Receiver']}<br>Possession: {row['possession_ID']}"],
                hoverinfo="text",
                showlegend=False
            ))

            # Draw the end marker if needed
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
                    text=[f"Thrower: {row['Thrower']}<br>Receiver: {row['Receiver']}<br>Possession: {row['possession_ID']}"],
                    hoverinfo="text",
                    showlegend=False
                ))
        
        st.plotly_chart(fig, use_container_width=True)
    with col_legend:
        st.markdown("<br><br><br><br><br><br><br><br><br><br><br><br><br><br><br><br>", unsafe_allow_html=True)
        show_custom_legend() 
    st.dataframe(df)       


def show_blocks(df):
    fig = draw_field()
    location_x = df['Location X (0 -> 1 = left sideline -> right sideline)'].apply(norm_to_field_x)
    location_y = df['Location Y (0 -> 1 = back of opponent endzone -> back of own endzone)'].apply(norm_to_field_y)
    fig.add_trace(go.Scatter(
        x=location_x,
        y=location_y,
        mode='markers',
        marker=dict(size=16, color='red', symbol='circle'),
        name='Block',
        hoverinfo='text',
        text=df['Player']
    ))
    st.plotly_chart(fig, use_container_width=False)

def show_endzone_attempts(df):
    # For each unique (Point, Possession), remove all throws that occur before the first time the disc has a start of Y < 0.36363
    # Assumes columns: 'Point', 'Possession', 'Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'
    filtered_rows = []
    for (tournament_game, point, possession), group in df.groupby(['tournament_game', 'Point', 'Possession']):
        # Find the index of the first throw with start Y < 0.36363
        mask = group['Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'] < 0.36363
        if mask.any():
            first_idx = mask.idxmax()  # idxmax returns the first index where mask is True
            # Keep all throws from first_idx onwards (including first_idx)
            group = group.loc[first_idx:]
            filtered_rows.append(group)
        # If no such throw, skip this group entirely
    df = pd.concat(filtered_rows) if filtered_rows else df.iloc[0:0]


    st.markdown("#### Endzone Attempts")
    st.markdown("Defined as any possession where the disc has moved within 20 yards of the endzone.")

    num_points_with_clean_ez_scores = 0
    num_points_with_dirty_ez_scores = 0
    num_points_broken = 0

    points_with_endzone_attempts = df.groupby(['tournament_game', 'Point'])
    num_points_with_endzone_attempts = points_with_endzone_attempts.ngroups

    for point, point_data in points_with_endzone_attempts:
        if (point_data['Assist?'] == 1).any():
            # We scored
            if point_data['Possession'].nunique() == 1:
                num_points_with_clean_ez_scores += 1
            else:
                num_points_with_dirty_ez_scores += 1
        else:
            num_points_broken += 1
    
    clean_pct = f"{(num_points_with_clean_ez_scores / num_points_with_endzone_attempts * 100):.1f}%" if num_points_with_endzone_attempts > 0 else None
    dirty_pct = f"{(num_points_with_dirty_ez_scores / num_points_with_endzone_attempts * 100):.1f}%" if num_points_with_endzone_attempts > 0 else None
    broken_pct = f"{(num_points_broken / num_points_with_endzone_attempts * 100):.1f}%" if num_points_with_endzone_attempts > 0 else None

    # num_unique_possessions_with_endzone_attempts = df.groupby(['tournament_game', 'Point', 'Possession']).ngroups


    # TODO: Add a way to view clean ez scores, dirty ez scores, and ez attempts --> broken via buttons
    # Instead of the specific point selection

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Num Points Clean EZ Scores", value=num_points_with_clean_ez_scores)
        st.badge(clean_pct, color="green")
        st.metric(label="Num Points w/EZ Attempts", value=num_points_with_endzone_attempts)
        
    with col2:
        st.metric(label="Num Points Dirty EZ Scores", value=num_points_with_dirty_ez_scores)
        st.badge(dirty_pct, color="orange")
        # st.metric(label="Total # EZ Attempts", value=num_unique_possessions_with_endzone_attempts)
    with col3:
        st.metric(label="Num Points EZ Attempt -> Broken", value=num_points_broken)
        st.badge(broken_pct, color="red")


    # Visualization
    fig = draw_field()
    # Create a unique list of (tournament_game, Point) tuples for selection
    unique_points = df[['tournament_game', 'Point']].drop_duplicates()
    unique_points_list = [
        (row['tournament_game'], row['Point']) for _, row in unique_points.iterrows()
    ]
    # Format for display
    point_labels = [
        f"{tournament_game} - Point {point}" for tournament_game, point in unique_points_list
    ]
    point_selection = st.selectbox(
        'Point',
        options=list(zip(point_labels, unique_points_list)),
        index=None,
        format_func=lambda x: x[0] if x else "Select a point",
        placeholder='Select a point'
    )
    if point_selection:
        selected_tournament_game, selected_point = point_selection[1]
        df = df[(df['tournament_game'] == selected_tournament_game) & (df['Point'] == selected_point)]

    # # Prepare throw start and end points
    start_x = df['Start X (0 -> 1 = left sideline -> right sideline)'].apply(norm_to_field_x)
    start_y = df['Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'].apply(norm_to_field_y)
    end_x = df['End X (0 -> 1 = left sideline -> right sideline)'].apply(norm_to_field_x)
    end_y = df['End Y (0 -> 1 = back of opponent endzone -> back of own endzone)'].apply(norm_to_field_y)

    # Add throws as arrows
    for index, row in df.iterrows():
        sx = norm_to_field_x(row['Start X (0 -> 1 = left sideline -> right sideline)'])
        sy = norm_to_field_y(row['Start Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
        ex = norm_to_field_x(row['End X (0 -> 1 = left sideline -> right sideline)'])
        ey = norm_to_field_y(row['End Y (0 -> 1 = back of opponent endzone -> back of own endzone)'])
        thrower = row['Thrower']
        receiver = row['Receiver']
        point = row['Point']
        turnover = row['Turnover?']
        thrower_error = row['Thrower error?']
        receiver_error = row['Receiver error?']

        end_shape = "circle"
        start_shape = "circle"
        color = "green"
        start_size = 3
        end_size = 3
        if turnover == 1:
            color = "red"
            if thrower_error == 1:
                start_shape = "square"
                start_size = 15
            if receiver_error == 1:
                end_shape = "square"
                end_size = 15

        # Draw the line (start to end)
        # Show thrower and receiver on hover for both endpoints and the line
        hover_text = f"Thrower: {thrower}<br>Receiver: {receiver}<br>Possession: {row.get('Possession', '')}"
        fig.add_trace(go.Scatter(
            x=[sx, ex],
            y=[sy, ey],
            mode="lines+markers",
            line=dict(color=color, width=2),
            marker=dict(
                size=[start_size, end_size],
                color=[color, color],
                symbol=[start_shape, end_shape]
            ),
            hoverinfo="text",
            text=[hover_text, hover_text],
            showlegend=False
        ))
        # Add arrow head
        fig.add_annotation(
            x=ex, y=ey,
            ax=sx, ay=sy,
            xref="x", yref="y", axref="x", ayref="y",
            showarrow=True,
            arrowhead=3,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor=color,
            opacity=0.7
        )
    st.plotly_chart(fig, use_container_width=False)
    st.dataframe(df)