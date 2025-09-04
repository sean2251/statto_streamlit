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

def update_selected_thrower(thrower_name, selected):
    print("update_selected_thrower", thrower_name, selected)
    pass

def update_all_throwers(all_throwers_selected):
    st.session_state['all_throwers_selected'] = not st.session_state['all_throwers_selected']
    for thrower in st.session_state['selected_throwers']:
        st.session_state['selected_throwers'][thrower] = st.session_state['all_throwers_selected']

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
