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
