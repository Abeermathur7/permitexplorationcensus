import streamlit as st
import numpy as np
import pandas as pd
import altair as alt

# Page title
st.set_page_config(page_title='Permit Data Exploration', page_icon='📊')
st.title('📊 Permit Data Exploration')

with st.expander('About this app'):
  st.markdown('**What can this app do?**')
  st.info('Interact with the permit dataset/Parquet files and explores each column.')
  st.markdown('**How to use the app?**')
  st.warning('Idk yet, this is a prototype')
  
st.subheader('Select a Construction Type')

# Load data

#--------------------------------------------------------------------------------------------------------------
df50 = pd.read_parquet('data/csv_reveal-gc-2020-50.parquet')
print(df50[:5])
df50.describe()

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

















































# df.year = df.year.astype('int')
#--------------------------------------------------------------------------------------------------------------
# Input widgets
## Genres selection
# genres_list = df.genre.unique()
# genres_selection = st.multiselect('Select genres', genres_list, ['Action', 'Adventure', 'Biography', 'Comedy', 'Drama', 'Horror'])

# ## Year selection
# year_list = df.year.unique()
# year_selection = st.slider('Select year duration', 1986, 2006, (2000, 2016))
# year_selection_list = list(np.arange(year_selection[0], year_selection[1]+1))

# df_selection = df[df.genre.isin(genres_selection) & df['year'].isin(year_selection_list)]
# reshaped_df = df_selection.pivot_table(index='year', columns='genre', values='gross', aggfunc='sum', fill_value=0)
# reshaped_df = reshaped_df.sort_values(by='year', ascending=False)


# # Display DataFrame

# df_editor = st.data_editor(reshaped_df, height=212, use_container_width=True,
#                             column_config={"year": st.column_config.TextColumn("Year")},
#                             num_rows="dynamic")
# df_chart = pd.melt(df_editor.reset_index(), id_vars='year', var_name='genre', value_name='gross')

# # Display chart
# chart = alt.Chart(df_chart).mark_line().encode(
#             x=alt.X('year:N', title='Year'),
#             y=alt.Y('gross:Q', title='Gross earnings ($)'),
#             color='genre:N'
#             ).properties(height=320)
# st.altair_chart(chart, use_container_width=True)
