import streamlit as st
import pandas as pd
import altair as alt
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
import numpy as np
from streamlit_echarts import st_echarts
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
jurisdiction_selection = st.multiselect('Select Jurisdictions', jurisdiction_list, jurisdiction_list[:3])

# Filter data based on selections
df_selection = df[
    df['CONST_TYPE'].isin(const_type_selection) &
    df['SITE_STATE'].isin(state_selection) &
    df['SITE_JURIS'].isin(jurisdiction_selection)
]

# Filter data based on selections
df_selection = df[df.CONST_TYPE.isin(const_type_selection) & df.SITE_STATE.isin(state_selection)]
# Summary Statistics
st.subheader('Summary Statistics')
total_permits = df_selection.shape[0]
total_value = df_selection['PMT_VALUE'].sum()
average_value = df_selection['PMT_VALUE'].mean()
max_value = df_selection['PMT_VALUE'].max()
min_value = df_selection['PMT_VALUE'].min()

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label='Total Permits', value=total_permits)
with col2:
    st.metric(label='Total Value', value=total_value)
with col3:
    st.metric(label='Average Value', value=average_value)
with col4:
    st.metric(label='Max Value', value=max_value)



# ECharts visualization
st.subheader('ECharts: Permit Values Over Time')

# Prepare data for ECharts
df_selection['PMT_WEEK'] = df_selection['PMT_WEEK'].astype(str)  # Ensure PMT_WEEK is a string for ECharts
chart_data = df_selection.groupby('PMT_WEEK')['PMT_VALUE'].sum().reset_index().sort_values('PMT_WEEK')
# Define ECharts options with text color customization
options = {
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "cross"
        },
        "textStyle": {
            "color": "black"  
        }
    },
    "legend": {
        "data": ["Permit Value"],
        "textStyle": {
            "color": "white"  
        }
    },
    "xAxis": {
        "type": "category",
        "data": chart_data['PMT_WEEK'].tolist(),
        "name": "Week",
        "axisLabel": {
            "rotate": 45,
            "fontSize": 10,
            "color": "white"  
        },
        "axisLine": {
            "lineStyle": {
                "color": "white"  
            }
        },
        "splitLine": {
            "show": False  
        }
    },
    "yAxis": {
        "type": "value",
        "name": "Permit Value",
        "axisLabel": {
            "fontSize": 10,
            "color": "white"  
        },
        "axisLine": {
            "lineStyle": {
                "color": "white"  
            }
        },
        "splitLine": {
            "lineStyle": {
                "color": "#333"  
            }
        }
    },
    "series": [
        {
            "name": "Permit Value",
            "data": chart_data['PMT_VALUE'].tolist(),
            "type": "line",
            "smooth": True,
            "areaStyle": {
                "color": {
                    "type": "linear",
                    "x": 0,
                    "y": 0,
                    "x2": 0,
                    "y2": 1,
                    "colorStops": [
                        {
                            "offset": 0,
                            "color": "rgba(0, 128, 255, 0.3)"  
                        },
                        {
                            "offset": 1,
                            "color": "rgba(0, 128, 255, 0)"  
                        }
                    ]
                }
            },
            "lineStyle": {
                "width": 2,
                "color": "blue"
            },
            "itemStyle": {
               "color": "#40E0D0" 
            },
            "showSymbol": True,
            "symbol": "circle",
            "symbolSize": 8
        }
    ],
    "dataZoom": [
        {
            "type": "inside",
            "start": 0,
            "end": 100
        }
    ],
    "title": {
        "text": "Permit Values Over Time",
        "textStyle": {
            "color": "White"  
        }
    }
}

st_echarts(options=options, height="400px")


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


# Pivot table to aggregate data
reshaped_df = df_selection.pivot_table(index='SITE_STATE', columns='CONST_TYPE', values='PERMITID', aggfunc='count', fill_value=0)
reshaped_df = reshaped_df.sort_values(by='SITE_STATE', ascending=False)
df_chart = reshaped_df.reset_index().melt(id_vars='SITE_STATE', var_name='CONST_TYPE', value_name='COUNT')

# Define ECharts options for the bar chart
bar_chart_options = {
    "tooltip": {
        "trigger": "axis",
        "axisPointer": {
            "type": "shadow"
        }
    },
    "legend": {
        "data": df_chart['CONST_TYPE'].unique().tolist(),
        "textStyle": {
            "fontSize": 12,
            "color": "white"
        }
    },
    "xAxis": {
        "type": "category",
        "data": df_chart['SITE_STATE'].tolist(),
        "name": "State",
        "axisLabel": {
            "rotate": 45,
            "fontSize": 10,
            "color": "white"
        }
    },
    "yAxis": {
        "type": "value",
        "name": "Permit Count",
        "axisLabel": {
            "fontSize": 10,
            "color": "white"
        }
    },
    "series": [
        {
            "name": const_type,
            "type": "bar",
            "data": df_chart[df_chart['CONST_TYPE'] == const_type]['COUNT'].tolist()
        }
        for const_type in df_chart['CONST_TYPE'].unique().tolist()
    ]
}

# Display the ECharts bar chart
st_echarts(options=bar_chart_options, height="400px")



####################################################################################











# Calculate month lag
df_selection['CREATEDATE'] = pd.to_datetime(df_selection['CREATEDATE'])
df_selection['PMT_DATE'] = pd.to_datetime(df_selection['PMT_DATE'])
df_selection['MONTH_LAG'] = (df_selection['CREATEDATE'] - df_selection['PMT_DATE']).dt.days // 30

# Summarize units by survey month and jurisdiction
df_unitFilter = df_selection[df_selection['PMT_UNITS']>0&
    df_selection['SITE_JURIS'].isin(jurisdiction_selection) ]


df_unitFilter['SURVEY_MONTH'] = df_selection['PMT_DATE'].dt.to_period('M').dt.to_timestamp()
df_summarized = df_unitFilter.groupby(['SURVEY_MONTH', 'SITE_JURIS', 'MONTH_LAG']).agg({'PMT_UNITS': 'sum'}).reset_index()



chart_data = df_summarized.rename(columns={
    'SURVEY_MONTH': 'Month',
    'SITE_JURIS': 'Jurisdiction',
    'MONTH_LAG': 'Month Lag',
    'PMT_UNITS': 'Units'
})
######################################################################

max_month_lag = chart_data.groupby('Jurisdiction')['Month Lag'].max().reset_index()
max_month_lag_jurisdiction = max_month_lag.loc[max_month_lag['Month Lag'].idxmax()]

# Create a two-column layout
col1, col2 = st.columns([3, 1])

# Column 1: Render the bar chart
with col1:
    grouped_bar_chart = alt.Chart(chart_data).mark_bar().encode(
        x=alt.X('Month:T', title='Month', timeUnit='yearmonth', axis=alt.Axis(format='%b %Y')),
        y=alt.Y('sum(Units):Q', title='Sum of Units'),
        color=alt.Color('Jurisdiction:N', legend=alt.Legend(title="Jurisdiction")),
        tooltip=['Month:T', 'sum(Units):Q', 'Jurisdiction:N', 'Month Lag:Q']
    ).properties(
        width= 200,
        height=100
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

    st.altair_chart(grouped_bar_chart)

# Column 2: Display key metrics
with col2:
    st.write("## Key Metrics")
    st.metric(label="Maximum Month Lag", value=int(max_month_lag_jurisdiction['Month Lag']))
    st.metric(label="Jurisdiction with Maximum Month Lag", value=max_month_lag_jurisdiction['Jurisdiction'])

    # Optionally, add more metrics here
    total_units = chart_data['Units'].sum()
    avg_month_lag = chart_data['Month Lag'].mean()
    st.metric(label="Total Units", value=int(total_units))
    st.metric(label="Average Month Lag", value=round(avg_month_lag, 2))

# Vega-Lite chart for Permit Units vs. Construction Type

# Faceted stacked bar chart options