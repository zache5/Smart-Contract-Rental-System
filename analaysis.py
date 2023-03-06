import streamlit as st
import pandas as pd
import plotly.express as px
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid import GridUpdateMode, DataReturnMode

st.title('CSV Analysis')
st.subheader('Before uploading your CSV file, please make sure that the file has columns name such as "Pickup Date" and "Return Date"')
st.write('Upload your csv file')


uploaded_file = st.file_uploader(
    "",
    key="1")

if uploaded_file is not None:
    file_container = st.expander("Check your uploaded .csv")
    df = pd.read_csv(uploaded_file)
    uploaded_file.seek(0)
    file_container.write(df)

    # Get date range for filtering
    min_date = pd.to_datetime(df['Pickup Date']).min().date()
    max_date = pd.to_datetime(df['Return Date']).max().date()
    selected_date = st.date_input('Select a date:', value=min_date, min_value=min_date, max_value=max_date)

    # Filter the dataframe by selected date for pickups
    pickups_df = df[(pd.to_datetime(df['Pickup Date']).dt.date == selected_date)]
    pickups_count = pickups_df.shape[0]

    # Filter the dataframe by selected date for returns
    returns_df = df[(pd.to_datetime(df['Return Date']).dt.date == selected_date)]
    returns_count = returns_df.shape[0]

    st.subheader(f"Number of mopeds picked on {selected_date}: {pickups_count}")
    st.subheader(f"Number of mopeds returned on {selected_date}: {returns_count}")

    # Display the chart
    fig = px.bar(x=["Pickups", "Returns"], y=[pickups_count, returns_count], labels={'x':'', 'y':'Count'})
    st.plotly_chart(fig)

    gb = GridOptionsBuilder.from_dataframe(df)
    # enables pivoting on all columns, however i'd need to change ag grid to allow export of pivoted/grouped data, however it select/filters groups
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
    gb.configure_side_bar()  # side_bar is clearly a typo :) should by sidebar
    gridOptions = gb.build()

    response = AgGrid(
    df,
    gridOptions=gridOptions,
    enable_enterprise_modules=True,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=False,
    )

    df = pd.DataFrame(response["selected_rows"])

    st.subheader("Filtered data will appear below ")
    st.text("")

    st.table(df)

    st.text("")

    c29, c30, c31 = st.columns([1, 1, 2])
