import streamlit as st
import pandas as pd
import plotly.graph_objects as go

FIELD_LENGTH = 110  # total length (including both endzones)
FIELD_WIDTH = 40    # width (sideline to sideline)
ENDZONE_DEPTH = 20  # each endzone


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
    fig = draw_field()

    # TODO: When thrower / receiver is selected, show thrower stats (yards, completions, etc)
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

    # Prepare throw start and end points
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
        hover_text = f"Thrower: {thrower}<br>Receiver: {receiver}"
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
        hover_text = f"Thrower: {thrower}<br>Receiver: {receiver}"
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