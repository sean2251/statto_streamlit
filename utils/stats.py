import streamlit as st

def show_points(df):
    o_points = df[df['Started on offense?'] == 1]
    total_o_points = len(o_points)

    clean_holds = o_points[(o_points['Scored?'] == 1) & (o_points['Possessions'] == 1)]
    num_clean_holds = len(clean_holds)
    pct_clean_holds = f"{(num_clean_holds / total_o_points * 100):.1f}%"

    dirty_holds = o_points[(o_points['Scored?'] == 1) & (o_points['Possessions'] > 1)]
    num_dirty_holds = len(dirty_holds)
    pct_dirty_holds = f"{(num_dirty_holds / total_o_points * 100):.1f}%"

    o_broken = o_points[o_points['Scored?'] == 0]
    num_o_broken = len(o_broken)
    pct_o_broken = f"{(num_o_broken / total_o_points * 100):.1f}%"

    st.markdown("#### Offensive Point Outcomes")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Clean Holds", value=num_clean_holds)
        st.badge(pct_clean_holds, color="green")
        st.metric(label="Total O Points", value=total_o_points)
    with col2:
        st.metric(label="Dirty Holds", value=num_dirty_holds)
        st.badge(pct_dirty_holds, color="orange")
    with col3:
        st.metric(label="Broken", value=num_o_broken)
        st.badge(pct_o_broken, color="red")

    d_points = df[df['Started on offense?'] == 0]
    total_d_points = len(d_points)

    num_d_points_with_break_chance = len(d_points[d_points['Possessions'] > 0])
    pct_points_with_break_chance = f"{(num_d_points_with_break_chance / total_d_points * 100):.1f}%"

    total_break_chances = d_points['Possessions'].sum()
    num_breaks = len(d_points[d_points['Scored?'] == 1])

    num_clean_breaks = len(d_points[(d_points['Scored?'] == 1) & (d_points['Possessions'] == 1)])
    num_dirty_breaks = len(d_points[(d_points['Scored?'] == 1) & (d_points['Possessions'] > 1)])


    st.markdown("#### Defensive Point Outcomes")
    st.markdown("*Break chance generation*")
    col1, col2 = st.columns(2)
    col1.metric(label="Points w/Break Chance", value=num_d_points_with_break_chance)
    col1.badge(pct_points_with_break_chance, color="green")
    col2.metric(label="Total D Points", value=total_d_points)


    st.markdown("*Conversion (relative to points w/break chance)*")
    col1, col2, col3 = st.columns(3)
    with col1:
        # clean breaks
        st.metric(label="Clean Breaks", value=num_clean_breaks)
        pct_clean_break_points = f"{(num_clean_breaks / num_d_points_with_break_chance * 100):.1f}%"
        st.badge(f"{pct_clean_break_points}", color="green")
    with col2:
        st.metric(label="Dirty Breaks", value=num_dirty_breaks)
        pct_dirty_break_points = f"{(num_dirty_breaks / num_d_points_with_break_chance * 100):.1f}%"
        st.badge(f"{pct_dirty_break_points}", color="orange")
    with col3:
        st.metric(label="Break Chance(s) Not Converted", value=num_d_points_with_break_chance - num_breaks)
        pct_not_converted = f"{(num_d_points_with_break_chance - num_breaks) / num_d_points_with_break_chance * 100:.1f}%"
        st.badge(f"{pct_not_converted}", color="red")


    with st.expander("*Conversion (relative to all break chances)*"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Break Chances", value=total_break_chances)
        with col2:
            st.metric('Converted Break Chances', value = num_breaks)
            pct_converted = f"{(num_breaks / total_break_chances * 100):.1f}%"
            st.badge(f"{pct_converted}", color="green")
        with col3:
            st.metric(label="DOffensive Turnovers", value=total_break_chances - num_breaks)
            pct_turnovers = f"{(total_break_chances - num_breaks) / total_break_chances * 100:.1f}%"
            st.badge(f"{pct_turnovers}", color="red")
