import streamlit as st
import pandas as pd

def group_player_stats_df(df):
    df = df.drop(columns=[
        "Points played", 
        "Average completed throw distance (m)",
        "Average completed throw gain (m)",
        "Average caught pass distance (m)",
        "Average caught pass gain (m)"
        ], axis=1)
    df = df.groupby("Player").sum().reset_index()
    return df

def create_involvement_df(psdf):
    involvement_df = psdf[[
        "Player", 
        "Points played total", 
        "Offense points played", 
        "Offense points won",
        "Defense points played",
        "Defense points won",
        "Touches",
        "Points played with touches",
        "Turnovers",
        "Defensive blocks"
        ]]
    involvement_df.rename({
        "Points played total": "Total points played",
        "Offense points played": "O points played",
        "Offense points won": "O points won",
        "Defense points played": "D points played",
        "Defense points won": "D points won",
    }, axis=1, inplace=True)
    involvement_df['Point win %'] = ((involvement_df['O points won'] + involvement_df['D points won']) / involvement_df['Total points played'] * 100).round(1)
    involvement_df['O point win %'] = (involvement_df['O points won'] / involvement_df['O points played'] * 100).round(1)
    involvement_df['D point win %'] = (involvement_df['D points won'] / involvement_df['D points played'] * 100).round(1)
    involvement_df['% points with touches'] = (involvement_df['Points played with touches'] / involvement_df['Total points played'] * 100).round(1)
    involvement_df['Blocks per point'] = (involvement_df['Defensive blocks'] / involvement_df['Total points played']).round(2)
    involvement_df['+/-'] = psdf['Goals'] + psdf['Assists'] + (0.5 * psdf['Secondary assists']) + psdf['Defensive blocks'] - psdf['Turnovers']
    return involvement_df

def create_throwing_df(psdf):
    throwing_df = psdf[[
        "Player",
        "Throws",
        "Thrower errors",
        "Assists",
        "Secondary assists",
        "Possessions initiated",
        "Total completed throw distance (m)",
        "Total completed throw gain (m)",
    ]]
    throwing_df['Total completed throw distance (m)'] = (throwing_df['Total completed throw distance (m)'] * 1.09361).round(2)
    throwing_df['Total completed throw gain (m)'] = (throwing_df['Total completed throw gain (m)'] * 1.09361).round(2)
    throwing_df.rename({
        "Assists": "A1",
        "Secondary assists": "A2",
        "Total completed throw distance (m)": "Total completed throw distance (yd)",
        "Total completed throw gain (m)": "Total completed throw gain (yd)",
    }, axis=1, inplace=True)
    completion_pct = ((throwing_df['Throws'] - throwing_df['Thrower errors'])/ throwing_df['Throws'] * 100).round(1)
    throwing_df.insert(3, 'Throw completion %', completion_pct)
    throwing_df['Avg completed throw distance (yd)'] = (throwing_df['Total completed throw distance (yd)'] / (throwing_df['Throws'] - throwing_df['Thrower errors'])).round(1)
    throwing_df['Avg completed throw gain (yd)'] = (throwing_df['Total completed throw gain (yd)'] / (throwing_df['Throws'] - throwing_df['Thrower errors'])).round(1)
    return throwing_df

def create_advanced_throwing_df(psdf, passes_df):
    df = pd.DataFrame()
    df['Player'] = psdf['Player'].unique()

    stats_1 = []
    stats_2 = []

    for player in df['Player']:
        player_passes = passes_df[passes_df['Thrower'] == player]
        num_throws = len(player_passes)
        throw_completions = player_passes[player_passes['Turnover?'] == 0].shape[0]
        throw_completion_pct = round((throw_completions / num_throws) * 100, 2) if num_throws > 0 else 0.0

        num_hucks = player_passes[player_passes['Huck?'] == 1].shape[0]
        huck_completions = player_passes[(player_passes['Huck?'] == 1) & (player_passes['Turnover?'] == 0)].shape[0]
        huck_completion_pct = round((huck_completions / num_hucks) * 100, 2) if num_hucks > 0 else 0.0

        num_non_hucks = player_passes[player_passes['Huck?'] == 0].shape[0]
        non_huck_completions = player_passes[(player_passes['Huck?'] == 0) & (player_passes['Turnover?'] == 0)].shape[0]
        non_huck_completion_pct = round((non_huck_completions / num_non_hucks) * 100, 2) if num_non_hucks > 0 else 0.0

        assist_attempts = player_passes[player_passes['Throw to endzone?'] == 1]
        assist_completions = player_passes[(player_passes['Throw to endzone?'] == 1) & (player_passes['Turnover?'] == 0)].shape[0]
        assist_completion_pct = round((assist_completions / len(assist_attempts)) * 100, 2) if len(assist_attempts) > 0 else 0.0

        stats_1.append({
            'Player': player,
            'Throws': num_throws,
            '# huck attempts (>30 yd)': num_hucks,
            '# completed hucks': huck_completions,
            '# short pass attempts (<=30 yd)': num_non_hucks,
            '# completed short passes': non_huck_completions,
            'Assist attempts': len(assist_attempts),
            'Assist completions': assist_completions,
            'Overall %': throw_completion_pct,
            'Huck %': huck_completion_pct,
            'Short pass %': non_huck_completion_pct,
            'Assist %': assist_completion_pct,
        })

        near_sideline_throws = player_passes[player_passes['From sideline?'] == 1]
        near_sideline_completions = player_passes[(player_passes['From sideline?'] == 1) & (player_passes['Turnover?'] == 0)].shape[0]
        near_sideline_throw_pct = round((near_sideline_completions / len(near_sideline_throws)) * 100, 2) if len(near_sideline_throws) > 0 else 0.0

        center_throws = player_passes[player_passes['From sideline?'] == 0]
        center_completions = player_passes[(player_passes['From sideline?'] == 0) & (player_passes['Turnover?'] == 0)].shape[0]
        center_throw_pct = round((center_completions / len(center_throws)) * 100, 2) if len(center_throws) > 0 else 0.0

        stats_2.append({
            'Player': player,
            'Throws': num_throws,
            'Throws from sideline (within 6yd)': len(near_sideline_throws),
            'Sideline throw completions': near_sideline_completions,
            '# center throws (>6yd from sideline)': len(center_throws),
            'Center throw completions': center_completions,
            'Overall %': throw_completion_pct,
            'Sideline throw %': near_sideline_throw_pct,
            'Center throw %': center_throw_pct,
        })

    df1 = pd.DataFrame(stats_1)
    df2 = pd.DataFrame(stats_2)

    return df1, df2

def show_team_throwing_stats(passes_df):
    # Calculate teamwide throwing completion rates
    team_stats = []

    # Overall throw completion rate
    total_throws = passes_df.shape[0]
    total_completions = passes_df[passes_df['Turnover?'] == 0].shape[0]
    overall_completion_pct = round((total_completions / total_throws) * 100, 2) if total_throws > 0 else 0.0

    # Huck completion rate
    total_huck_attempts = passes_df[passes_df['Huck?'] == 1].shape[0]
    total_huck_completions = passes_df[(passes_df['Huck?'] == 1) & (passes_df['Turnover?'] == 0)].shape[0]
    huck_completion_pct = round((total_huck_completions / total_huck_attempts) * 100, 2) if total_huck_attempts > 0 else 0.0

    # Non-huck completion rate
    total_non_huck_attempts = passes_df[passes_df['Huck?'] == 0].shape[0]
    total_non_huck_completions = passes_df[(passes_df['Huck?'] == 0) & (passes_df['Turnover?'] == 0)].shape[0]
    non_huck_completion_pct = round((total_non_huck_completions / total_non_huck_attempts) * 100, 2) if total_non_huck_attempts > 0 else 0.0

    # Sideline throw completion rate
    total_sideline_attempts = passes_df[passes_df['From sideline?'] == 1].shape[0]
    total_sideline_completions = passes_df[(passes_df['From sideline?'] == 1) & (passes_df['Turnover?'] == 0)].shape[0]
    sideline_completion_pct = round((total_sideline_completions / total_sideline_attempts) * 100, 2) if total_sideline_attempts > 0 else 0.0

    # Center throw completion rate
    total_center_attempts = passes_df[passes_df['From sideline?'] == 0].shape[0]
    total_center_completions = passes_df[(passes_df['From sideline?'] == 0) & (passes_df['Turnover?'] == 0)].shape[0]
    center_completion_pct = round((total_center_completions / total_center_attempts) * 100, 2) if total_center_attempts > 0 else 0.0

    # Assist attempt completion rate
    total_assist_attempts = passes_df[passes_df['Throw to endzone?'] == 1].shape[0]
    total_assist_completions = passes_df[(passes_df['Throw to endzone?'] == 1) & (passes_df['Turnover?'] == 0)].shape[0]
    assist_completion_pct = round((total_assist_completions / total_assist_attempts) * 100, 2) if total_assist_attempts > 0 else 0.0

    team_stats.append({
        'Player': 'Team Total',
        'Throws': total_throws,
        'Overall completions': total_completions,
        'Overall completion %': overall_completion_pct,
        '# huck attempts (>30 yd)': total_huck_attempts,
        'Huck completions': total_huck_completions,
        'Huck %': huck_completion_pct,
        '# short pass attempts (<=30 yd)': total_non_huck_attempts,
        'Short pass completions': total_non_huck_completions,
        'Short pass %': non_huck_completion_pct,
        'Throws from sideline (within 6yd)': total_sideline_attempts,
        'Sideline throw completions': total_sideline_completions,
        'Sideline throw %': sideline_completion_pct,
        '# center throws (>6yd from sideline)': total_center_attempts,
        'Center throw completions': total_center_completions,
        'Center throw %': center_completion_pct,
        'Assist attempts': total_assist_attempts,
        'Assist completions': total_assist_completions,
        'Assist %': assist_completion_pct,
    })
    team = team_stats[0]

    col1, col2, col3, col4, col5, col6 = st.columns(6, border=True)
    with col1:
        st.metric("Throws", team['Throws'])
        st.metric("Overall completions", team['Overall completions'])
        st.metric("Overall completion %", str(team['Overall completion %']))
    with col2:
        st.metric("Huck attempts (>30yd)", f"{team['# huck attempts (>30 yd)']} ({round((team['# huck attempts (>30 yd)'] / team['Throws'] * 100), 2)}%)")
        st.metric("Huck completions", str(team['Huck completions']))
        st.metric("Huck completion %", str(team['Huck %']))
    with col3:
        st.metric("Short pass attempts (<30yd)", f"{team['# short pass attempts (<=30 yd)']} ({round((team['# short pass attempts (<=30 yd)'] / team['Throws'] * 100), 2)}%)")
        st.metric("Short pass completions", str(team['Short pass completions']))
        st.metric("Short pass completion %", str(team['Short pass %'])) 
    with col4:
        st.metric("Assist attempts", f"{team['Assist attempts']} ({round((team['Assist attempts'] / team['Throws'] * 100), 2)}%)")
        st.metric("Assist completions", team['Assist completions'])
        st.metric("Assist completion %", str(team['Assist %']))
    with col5:
        st.metric("Throws from sideline (<6yd)", f"{team['Throws from sideline (within 6yd)']} ({round((team['Throws from sideline (within 6yd)'] / team['Throws'] * 100), 2)}%)")
        st.metric("Sideline completions", team['Sideline throw completions'])
        st.metric("Sideline completion %", str(team['Sideline throw %']))
    with col6:
        st.metric("Throws from center (>6yd from sideline)", f"{team['# center throws (>6yd from sideline)']} ({round((team['# center throws (>6yd from sideline)'] / team['Throws'] * 100), 2)}%)")
        st.metric("Center completions", team['Center throw completions'])
        st.metric("Center completion %", str(team['Center throw %']))  
    
    col1, col2, col3, col4, col5, col6 = st.columns(6, border=True)
    with col1:
        st.metric("Turnovers", passes_df['Turnover?'].sum())
    with col2:
        st.metric("Huck turnovers", passes_df[(passes_df['Huck?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0])
        st.metric(f"% of all turnovers", f"{round((passes_df[(passes_df['Huck?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0] / passes_df['Turnover?'].sum() * 100), 2) if passes_df['Turnover?'].sum() > 0 else 0.0}%")
    with col3:
        st.metric("Short pass turnovers", passes_df[(passes_df['Huck?'] == 0) & (passes_df['Turnover?'] == 1)].shape[0])
        st.metric(f"% of all turnovers", f"{round((passes_df[(passes_df['Huck?'] == 0) & (passes_df['Turnover?'] == 1)].shape[0] / passes_df['Turnover?'].sum() * 100), 2) if passes_df['Turnover?'].sum() > 0 else 0.0}%")
    with col4:
        st.metric("Assist turnovers", passes_df[(passes_df['Throw to endzone?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0])
        st.metric(f"% of all turnovers", f"{round((passes_df[(passes_df['Throw to endzone?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0] / passes_df['Turnover?'].sum() * 100), 2) if passes_df['Turnover?'].sum() > 0 else 0.0}%")
    with col5:
        st.metric("Turnovers from sideline (<6yd)", passes_df[(passes_df['From sideline?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0])
        st.metric(f"% of all turnovers", f"{round((passes_df[(passes_df['From sideline?'] == 1) & (passes_df['Turnover?'] == 1)].shape[0] / passes_df['Turnover?'].sum() * 100), 2) if passes_df['Turnover?'].sum() > 0 else 0.0}%")
    with col6:
        st.metric("Turnovers from center (>6yd from sideline)", passes_df[(passes_df['From sideline?'] == 0) & (passes_df['Turnover?'] == 1)].shape[0])
        st.metric(f"% of all turnovers", f"{round((passes_df[(passes_df['From sideline?'] == 0) & (passes_df['Turnover?'] == 1)].shape[0] / passes_df['Turnover?'].sum() * 100), 2) if passes_df['Turnover?'].sum() > 0 else 0.0}%")

def show_receiving_stats(psdf, passes_df):
    df = pd.DataFrame()
    df['Player'] = psdf['Player'].unique()

    stats = []
    st.dataframe(passes_df, width="content", hide_index=True)

    for player in df['Player']:
        player_catch_attempts = passes_df[passes_df['Receiver'] == player]
        num_catch_attempts = len(player_catch_attempts)
        num_catches = player_catch_attempts[player_catch_attempts['Turnover?'] == 0].shape[0]
        num_drops = player_catch_attempts[(player_catch_attempts['Turnover?'] == 1) & (player_catch_attempts['Receiver error?'] == 1)].shape[0]
        all_catch_pct = round((num_catches / num_catch_attempts) * 100, 2) if num_catch_attempts > 0 else 0.0
        catch_pct = round((num_catches / (num_catches + num_drops)) * 100, 2) if num_catch_attempts > 0 else 0.0
        goals = psdf[psdf['Player'] == player]['Goals'].values[0]
        goals_per_catch_attempt = round((goals / num_catch_attempts), 2) if num_catch_attempts > 0 else 0.0
        total_caught_pass_distance = round(psdf[psdf['Player'] == player]['Total caught pass distance (m)'].values[0] * 1.09361, 2)
        total_caught_pass_gain = round(psdf[psdf['Player'] == player]['Total caught pass gain (m)'].values[0] * 1.09361, 2)
        avg_caught_pass_distance = round(total_caught_pass_distance / num_catches, 2) if num_catches > 0 else 0.0
        avg_caught_pass_gain = round(total_caught_pass_gain / num_catches, 2) if num_catches > 0 else 0.0

        stats.append({
            'Player': player,
            'Catch attempts': num_catch_attempts,
            'Catches': num_catches,
            'Drops': num_drops,
            'Catch % (good throws)': catch_pct,
            'Catch % (inc. bad throws)': all_catch_pct,
            'Goals': goals,
            'Goals per catch attempt': goals_per_catch_attempt,
            'Total caught pass distance (yd)': total_caught_pass_distance,
            'Total caught pass gain (yd)': total_caught_pass_gain,
            'Avg caught pass distance (yd)': avg_caught_pass_distance,
            'Avg caught pass gain (yd)': avg_caught_pass_gain,
        })

    st.dataframe(pd.DataFrame(stats), width="content", hide_index=True)


def show_player_stats(passes_df, player_stats_df):
    st.markdown("*Tables include data from selected games on the left.*")
    grouped_psdf = group_player_stats_df(player_stats_df)

    involvement_df = create_involvement_df(grouped_psdf)
    with st.expander("Player Involvement - Points, touches, blocks, +/-", expanded=True):
        st.dataframe(involvement_df, width="content", hide_index=True)
    
    st.markdown("#### Throwing Stats")
    throwing_df = create_throwing_df(grouped_psdf)
    with st.expander("Player throws, A1/A2, initiation, throwing yardage", expanded=True):
            st.dataframe(throwing_df, width="content", hide_index=True)
    
    adf1, adf2 = create_advanced_throwing_df(grouped_psdf, passes_df)
    with st.expander("Player throw completion for hucks (>30yd), short passes, assists"):
        st.dataframe(adf1, width="content", hide_index=True)

    with st.expander("Player throw completion from sideline (<6yd)"):
        st.dataframe(adf2, width="content", hide_index=True)

    with st.expander("Team Throwing Stats - Hucks, assists, sideline throws", expanded=True):
        show_team_throwing_stats(passes_df)

    st.markdown("#### Receiving Stats")
    with st.expander("Player catches, goals, receiving yardage", expanded=True):
        show_receiving_stats(grouped_psdf, passes_df)
