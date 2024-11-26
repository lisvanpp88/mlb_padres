import streamlit as st
import pandas as pd

# Load data
hitters_data = pd.read_csv("hitters_data.csv")  # Hitters data
pitchers_data = pd.read_csv("pitchers_2024.csv")  # Pitchers data

# Get the list of full names
pitcher_names = pitchers_data['last_name, first_name'].tolist()

# Display the list for reference
#print(pitcher_names)

pitchers_data['Handedness'] = [
    'R', 'R', 'L', 'R', 'L', 'L', 'L', 'R', 'R', 'R', 'R', 'L', 'R', 'R', 'L', 'L', 'R', 'R', 'R', 'R', 'R', 'R', 'L', 'R', 
    'R', 'R', 'R', 'L', 'R', 'R', 'R', 'R', 'L', 'L', 'R', 'L', 'L', 'R', 'R', 'R', 'L', 'L', 'R', 'R', 'R', 'L', 'R', 'R', 'L', 
    'R', 'R', 'R', 'L', 'R', 'L', 'R', 'L', 'R', 'R', 'L', 'R', 'L', 'L', 'L', 'R', 'R', 'R', 'L', 'R', 'R', 'R', 'R', 'R', 'L', 
    'L', 'R', 'R', 'R', 'L', 'R', 'R', 'L', 'L', 'L', 'R', 'L', 'R', 'L', 'L', 'R', 'R', 'L', 'L', 'L', 'L', 'L', 'L', 'R', 'R', 
    'R', 'R', 'R', 'R', 'R', 'R', 'R', 'R'
]  # Replace this with the actual list

print(pitchers_data.columns)  # This will display how many rows your DataFrame has
#print(len(pitchers_handedness))  

# Calculate an approximate 'AVG' based on the available columns
pitchers_data['AVG vs RHH'] = pitchers_data.apply(
    lambda row: row['batting_avg'] if row['Handedness'] == 'R' else None, axis=1
)

pitchers_data['AVG vs LHH'] = pitchers_data.apply(
    lambda row: row['batting_avg'] if row['Handedness'] == 'L' else None, axis=1
)

hitters_data['AVG'] = hitters_data['avg_hit_speed'] / hitters_data['attempts']
hitters_data['SLG'] = (hitters_data['avg_hit_speed'] * hitters_data['brl_percent']) / 100

# Modify to calculate SLG vs RHH and SLG vs LHH with the available columns
pitchers_data['SLG vs RHH'] = pitchers_data['slg_percent']  # Using 'slg_percent' as an approximation
pitchers_data['SLG vs LHH'] = pitchers_data['slg_percent']  # Using 'slg_percent' as an approximation

# Verify pitchers_data columns
#print(hitters_data.columns)
#print(pitchers_data.head())

# Split the column 'last_name, first_name' into 'last_name' and 'first_name' in hitters_data
hitters_data[['last_name', 'first_name']] = hitters_data['last_name, first_name'].str.split(', ', expand=True)

# Drop the original column in hitters_data
hitters_data.drop(columns=['last_name, first_name'], inplace=True)

# Verify the first rows of hitters_data
#print(hitters_data.head())

# Continue with the rest of the code
st.title("Lineup Simulation - San Diego Padres 2024")
st.write("Simulate lineups and optimize performance against rival pitchers.")

# Select pitcher
st.sidebar.header("Select a pitcher")
pitcher_name = st.sidebar.selectbox("Pitcher:", pitchers_data['last_name, first_name'].unique())

# Selected pitcher's data
pitcher = pitchers_data[pitchers_data['last_name, first_name'] == pitcher_name].iloc[0]
st.sidebar.write(f"**Handedness:** {pitcher['Handedness']}")
st.sidebar.write(f"**AVG vs RHH:** {pitcher['AVG vs RHH']:.3f}")
st.sidebar.write(f"**AVG vs LHH:** {pitcher['AVG vs LHH']:.3f}")

# Configure lineup
st.header("Set up your lineup")
lineup = st.multiselect(
    "Select players for the lineup:",
    hitters_data['last_name'] + ", " + hitters_data['first_name'],
    default=(hitters_data['last_name'] + ", " + hitters_data['first_name']).iloc[:9]
)

# Configure bench
st.header("Select bench hitters")
bench = st.multiselect(
    "Select bench players (can be added to the lineup):",
    hitters_data['last_name'] + ", " + hitters_data['first_name'],
    default=[]
)

# Calculate adjusted scores
if lineup:
    # Create DataFrame with selected players
    lineup_data = hitters_data[(
        hitters_data['last_name'] + ", " + hitters_data['first_name']).isin(lineup)
    ].copy()
    # Assign batting order based on selection order
    lineup_data['batting_order'] = range(1, len(lineup_data) + 1)

    # Add bench players to the lineup (e.g., at the end or a selected position)
    if bench:
        bench_data = hitters_data[(
            hitters_data['last_name'] + ", " + hitters_data['first_name']).isin(bench)
        ].copy()

        # Optionally, add them to the end of the lineup or allow order change
        bench_data['batting_order'] = range(len(lineup_data) + 1, len(lineup_data) + len(bench_data) + 1)
        lineup_data = pd.concat([lineup_data, bench_data])

    # Display lineup with batting order
    st.subheader("Selected Lineup")
    st.write(lineup_data[['last_name', 'first_name', 'batting_order']])

    # Choose stats based on pitcher's handedness
    if pitcher['Handedness'] == 'R':  # Right-handed pitcher
        lineup_data['Pitcher_Adjusted_Score'] = (
            lineup_data['AVG'] * pitcher['AVG vs RHH'] +
            lineup_data['SLG'] * pitcher['SLG vs RHH']
        )
    else:  # Left-handed pitcher
        lineup_data['Pitcher_Adjusted_Score'] = (
            lineup_data['AVG'] * pitcher['AVG vs LHH'] +
            lineup_data['SLG'] * pitcher['SLG vs LHH']
        )

    # Show total score and lineup data
    st.subheader("Lineup Results")
    st.write(lineup_data[['last_name', 'first_name', 'batting_order', 'Pitcher_Adjusted_Score']])
    # Adjust the score based on batting order (e.g., top of the lineup gets a multiplier)
    lineup_data['Pitcher_Adjusted_Score'] *= lineup_data['batting_order'].apply(lambda x: 1.1 if x <= 3 else 1)

    total_score = lineup_data['Pitcher_Adjusted_Score'].sum()
    st.write(f"**Total Lineup Score:** {total_score:.2f}")

    # Visualization of individual scores
    st.bar_chart(lineup_data.set_index('last_name')['Pitcher_Adjusted_Score'])

    # Calculate total score
    total_score = lineup_data['Pitcher_Adjusted_Score'].sum()
    st.write(f"**Total Lineup Score:** {total_score:.2f}")
else:
    st.warning("Select at least one player to view performance.")
