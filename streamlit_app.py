import streamlit as st
import pandas as pd
import altair as alt
import folium
from folium.plugins import MarkerCluster

# Page title
st.set_page_config(page_title='Permit Data Exploration', page_icon='📊')
st.title('📊 Permit Data Exploration')

with st.expander('About this app'):
    st.markdown('**What can this app do?**')
    st.info('Interact with the permit dataset/Parquet files and explore each column.')
    st.markdown('**How to use the app?**')
    st.warning('This is a prototype, functionality will be added as we develop further.')

st.subheader('Explore Permit Data by Construction Type and State')

# Load data
df50 = pd.read_parquet('data/csv_reveal-gc-2020-50.parquet')

# Input widgets
## Construction Type selection
const_type_list = df50.CONST_TYPE.unique()
const_type_selection = st.multiselect('Select Construction Types', const_type_list, const_type_list[:3])

## State selection
state_list = df50.SITE_STATE.unique()
state_selection = st.multiselect('Select States', state_list, state_list[:3])

# Filter data based on selections
df_selection = df50[df50.CONST_TYPE.isin(const_type_selection) & df50.SITE_STATE.isin(state_selection)]

# Display DataFrame
st.dataframe(df_selection)

# Pivot table to aggregate data
reshaped_df = df_selection.pivot_table(index='SITE_STATE', columns='CONST_TYPE', values='PERMITID', aggfunc='count', fill_value=0)
reshaped_df = reshaped_df.sort_values(by='SITE_STATE', ascending=False)

# Display reshaped DataFrame
st.subheader('Aggregated Data by State and Construction Type')
st.dataframe(reshaped_df)

# Prepare data for chart
df_chart = reshaped_df.reset_index().melt(id_vars='SITE_STATE', var_name='CONST_TYPE', value_name='COUNT')

# Display chart
chart = alt.Chart(df_chart).mark_bar().encode(
            x=alt.X('SITE_STATE:N', title='State'),
            y=alt.Y('COUNT:Q', title='Permit Count'),
            color='CONST_TYPE:N'
            ).properties(height=320)
st.altair_chart(chart, use_container_width=True)

# Map visualization
st.subheader('Permit Locations Map')

# Clean data for map visualization
df_selection = df_selection.dropna(subset=['SITE_COOR1', 'SITE_DIR1'])
df_selection = df_selection[df_selection['SITE_COOR1'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
df_selection = df_selection[df_selection['SITE_DIR1'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
df_selection['SITE_COOR1'] = df_selection['SITE_COOR1'].astype(float)
df_selection['SITE_DIR1'] = df_selection['SITE_DIR1'].astype(float)

# Create a map centered on the average latitude and longitude
if not df_selection.empty:
    map_center = [df_selection['SITE_COOR1'].mean(), df_selection['SITE_DIR1'].mean()]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add marker cluster to the map
    marker_cluster = MarkerCluster().add_to(m)

    # Add points to the map
    for idx, row in df_selection.iterrows():
        folium.Marker(
            location=[row['SITE_COOR1'], row['SITE_DIR1']],
            popup=row['SITE_ADDRS']
        ).add_to(marker_cluster)

    # Save the map as an HTML file
    map_path = 'map.html'
    m.save(map_path)

    # Display the map in Streamlit
    with open(map_path, 'r') as f:
        html_map = f.read()
    st.components.v1.html(html_map, width=700, height=500)
else:
    st.write("No valid coordinates available for mapping.")

# Optional: Add more charts and statistics if necessary
# Example: Construction Type Distribution
st.subheader('Construction Type Distribution')
const_type_dist = df_selection['CONST_TYPE'].value_counts().reset_index()
const_type_dist.columns = ['CONST_TYPE', 'COUNT']

chart2 = alt.Chart(const_type_dist).mark_bar().encode(
    x=alt.X('CONST_TYPE:N', title='Construction Type'),
    y=alt.Y('COUNT:Q', title='Count'),
    color='CONST_TYPE:N'
).properties(height=320)
st.altair_chart(chart2, use_container_width=True)
