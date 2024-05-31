import streamlit as st
import pandas as pd
import altair as alt
import folium
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import st_folium

# Page title
st.set_page_config(page_title='Permit Data Exploration', page_icon='📊')
st.title('📊 Permit Data Exploration')

with st.expander('About this app'):
    st.markdown('**What can this app do?**')
    st.info('Interact with the permit dataset/Parquet files and explore each column.')
    st.markdown('**How to use the app?**')
    st.warning('This is a prototype, functionality will be added as we develop further.')

st.subheader('Explore Permit Data by Construction Type and State')

# File upload
uploaded_file = st.file_uploader("Upload your Parquet file", type=['parquet'])

if uploaded_file is not None:
    df = pd.read_parquet(uploaded_file)
else:
    df = pd.read_parquet('data/csv_reveal-gc-2020-50.parquet')

# Input widgets
## Construction Type selection
const_type_list = df.CONST_TYPE.unique()
const_type_selection = st.multiselect('Select Construction Types', const_type_list, const_type_list[:3])

## State selection
state_list = df.SITE_STATE.unique()
state_selection = st.multiselect('Select States', state_list, state_list[:3])

jurisdiction_list = df['SITE_JURIS'].unique().tolist()
jurisdiction_selection = st.multiselect('Select Jurisdictions', jurisdiction_list, jurisdiction_list[:3])

# Filter data based on selections
df_selection = df[
    df['CONST_TYPE'].isin(const_type_selection) &
    df['SITE_STATE'].isin(state_selection) &
    df['SITE_JURIS'].isin(jurisdiction_selection)
]

# Display DataFrame
st.dataframe(df_selection)
# Filter data based on selections
df_selection = df[df.CONST_TYPE.isin(const_type_selection) & df.SITE_STATE.isin(state_selection)]

# Summary Statistics
st.subheader('Summary Statistics')
st.write(df_selection.describe())

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
df_selection_map = df_selection[df_selection['SITE_LAT'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
df_selection_map = df_selection_map[df_selection_map['SITE_LONG'].apply(lambda x: str(x).replace('.', '', 1).lstrip('-').isdigit())]
df_selection_map['SITE_LAT1'] = df_selection_map['SITE_LAT'].astype(float)
df_selection_map['SITE_LONG1'] = df_selection_map['SITE_LONG'].astype(float)

# Create a Folium map centered on the average latitude and longitude
if not df_selection_map.empty:
    map_center = [df_selection_map['SITE_LAT1'].mean(), df_selection_map['SITE_LONG1'].mean()]
    m = folium.Map(location=map_center, zoom_start=5)

    # Add marker cluster to the map
    marker_cluster = MarkerCluster().add_to(m)

    # Add points to the map
    for idx, row in df_selection_map.iterrows():
        folium.Marker(
            location=[row['SITE_LAT1'], row['SITE_LONG1']],
            popup=row['PMT_VALUE']
        ).add_to(marker_cluster)

    # Call to render Folium map in Streamlit
    st_data = st_folium(m, width=800, height=500)

    # Display the map
    st.write('Permit Locations Map:')
    st.write(st_data)
else:
    st.write("No valid coordinates available for mapping.")