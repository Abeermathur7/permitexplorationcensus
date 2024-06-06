import streamlit as st
import pandas as pd
import altair as alt
import folium
from folium.plugins import MarkerCluster
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
d1 = pd.read_parquet('data/csv_reveal-gc-2020-41.parquet')
d2 = pd.read_parquet('data/csv_reveal-gc-2020-42.parquet')
d3 = pd.read_parquet('data/csv_reveal-gc-2020-43.parquet')
d4 = pd.read_parquet('data/csv_reveal-gc-2020-44.parquet')
d5 = pd.read_parquet('data/csv_reveal-gc-2020-45.parquet')
d6 = pd.read_parquet('data/csv_reveal-gc-2020-46.parquet')
d7 = pd.read_parquet('data/csv_reveal-gc-2020-47.parquet')
d8 = pd.read_parquet('data/csv_reveal-gc-2020-48.parquet')
d9 = pd.read_parquet('data/csv_reveal-gc-2020-49.parquet')
d50 = pd.read_parquet('data/csv_reveal-gc-2020-50.parquet')
df = pd.concat([d1, d2, d3, d4, d5, d6, d7, d8, d9], ignore_index=True)

# Input widgets
## Construction Type selection
const_type_list = df.CONST_TYPE.unique()
const_type_selection = st.multiselect('Select Construction Types', const_type_list, const_type_list[:3])

## State selection
state_list = df.SITE_STATE.unique()
state_selection = st.multiselect('Select States', state_list, state_list[:3])

jurisdiction_list = df['SITE_JURIS'].unique().tolist()
jurisdiction_selection = st.multiselect('Select Jurisdictions', jurisdiction_list, jurisdiction_list[:15])

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

# # Prepare data for chart
# df_chart = reshaped_df.reset_index().melt(id_vars='SITE_STATE', var_name='CONST_TYPE', value_name='COUNT')
# st.write(df_chart)
# # Display chart
# chart = alt.Chart(df_chart).mark_bar().encode(
#     x=alt.X('SITE_STATE:N', title='State'),
#     y=alt.Y('COUNT:Q', title='Permit Count'),
#     color='CONST_TYPE:N'
# ).properties(height=320)
# st.altair_chart(chart, use_container_width=True)


# # Map visualization
# st.subheader('Permit Locations Map')

# # Clean data for map visualization
# df_selection_map = df_selection[df_selection['SITE_LAT'].apply(lambda x: str(x).replace('.', '', 1).isdigit())]
# df_selection_map = df_selection_map[df_selection_map['SITE_LONG'].apply(lambda x: str(x).replace('.', '', 1).lstrip('-').isdigit())]
# df_selection_map['SITE_LAT1'] = df_selection_map['SITE_LAT'].astype(float)
# df_selection_map['SITE_LONG1'] = df_selection_map['SITE_LONG'].astype(float)

# # Create a Folium map centered on the average latitude and longitude
# if not df_selection_map.empty:
#     map_center = [df_selection_map['SITE_LAT1'].mean(), df_selection_map['SITE_LONG1'].mean()]
#     m = folium.Map(location=map_center, zoom_start=5)

#     # Add marker cluster to the map
#     marker_cluster = MarkerCluster().add_to(m)

#     # Add points to the map
#     for idx, row in df_selection_map.iterrows():
#         folium.Marker(
#             location=[row['SITE_LAT1'], row['SITE_LONG1']],
#             popup=row['PMT_VALUE']
#         ).add_to(marker_cluster)

#     # Call to render Folium map in Streamlit
#     st_data = st_folium(m, width=800, height=500)

#     # Display the map
#     st.write('Permit Locations Map:')
#     st.write(st_data)
# else:
#     st.write("No valid coordinates available for mapping.")

# Example
# import streamlit as st
# import pandas as pd
# import numpy as np
# import altair as alt

# if "data" not in st.session_state:
#     st.session_state.data = pd.DataFrame(
#         np.random.randn(20, 3), columns=["a", "b", "c"]
#     )
# df = st.session_state.data

# point_selector = alt.selection_point("point_selection")
# interval_selector = alt.selection_interval("interval_selection")
# chart = (
#     alt.Chart(df)
#     .mark_circle()
#     .encode(
#         x="a",
#         y="b",
#         size="c",
#         color="c",
#         tooltip=["a", "b", "c"],
#         fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3)),
#     )
#     .add_params(point_selector, interval_selector)
# )

# event = st.altair_chart(chart, key="alt_chart", on_select="rerun")

# event

st.subheader('Faceted Stacked Bar Chart of Permit Data')

# Calculate month lag
df_selection['CREATEDATE'] = pd.to_datetime(df_selection['CREATEDATE'])
df_selection['PMT_DATE'] = pd.to_datetime(df_selection['PMT_DATE'])
df_selection['MONTH_LAG'] = (df_selection['CREATEDATE'] - df_selection['PMT_DATE']).dt.days // 30

# Summarize units by survey month and jurisdiction
df_unitFilter = df_selection[df_selection['PMT_UNITS']>0]


df_unitFilter['SURVEY_MONTH'] = df_selection['PMT_DATE'].dt.to_period('M').dt.to_timestamp()
df_summarized = df_unitFilter.groupby(['SURVEY_MONTH', 'SITE_JURIS', 'MONTH_LAG']).agg({'PMT_UNITS': 'sum'}).reset_index()



chart_data = df_summarized.rename(columns={
    'SURVEY_MONTH': 'Month',
    'SITE_JURIS': 'Jurisdiction',
    'MONTH_LAG': 'Month Lag',
    'PMT_UNITS': 'Units'
})
######################################################################
# Simplified bar chart for debugging
grouped_bar_chart = alt.Chart(chart_data).mark_bar().encode(
    x=alt.X('Month:T', title='Month', timeUnit='yearmonth', axis=alt.Axis(format='%b %Y')),
    y=alt.Y('sum(Units):Q', title='Sum of Units'),
    color=alt.Color('Jurisdiction:N', legend=alt.Legend(title="Jurisdiction")),
    tooltip=['Month:T', 'sum(Units):Q', 'Jurisdiction:N', 'Month Lag:Q']
).properties(
    width=600,
    height=200
).facet(
    row=alt.Row('Month Lag:Q', header=alt.Header(title="Monthly Lag"))
).configure_axis(
    labelFontSize=12,
    titleFontSize=14
).configure_legend(
    labelFontSize=12,
    titleFontSize=14
).configure_facet(
    spacing=10  # Adjust spacing between facets
)

# Render the bar chart
st.altair_chart(grouped_bar_chart)

# 'Month Lag:Q', header=alt.Header(title="Monthly Lag")

#