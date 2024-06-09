import streamlit as st
import pandas as pd

st.set_page_config(page_title="PMS Performance Data Analysis", page_icon="📈", layout="wide")


# Load the data
aggregate_data = pd.read_csv('pms_performance_aggregate.csv')
monthly_data = pd.read_csv('pms_performance_monthly.csv')

# Create a multiselect box for aggregate_data
aggregate_options = aggregate_data.columns[1:]  # Exclude the 'Unnamed: 0' column


with st.sidebar:
    st.title('PMS Performance Data Analysis')
    st.write('## Select Options')
    selected_options = st.multiselect('Select options from aggregate data:', aggregate_options, default=['BANYAN TREE ADVISORS PRIVATE LIMITED', 'SECURITIES INVESTMENT MANAGEMENT PRIVATE LIMITED', 'MASTER PORTFOLIO SERVICES LTD', 'EQUITY INTELLIGENCE INDIA PVT. LTD.', 'MULTI-ACT EQUITY CONSULTANCY PVT LTD'])
    st.write('## Selected Options')
    # st.markdown(selected_options)

# Initialize an empty DataFrame to store the merged data of the selected options
selected_aggregate_data = pd.DataFrame()

# Loop through the selected options from aggregate_data
for option in selected_options:
    # Extract the 'Unnamed: 0' and the selected option columns from the data
    data = aggregate_data[['Unnamed: 0', option]].rename(columns={'Unnamed: 0': 'Parameter'})

    # Merge the data with merged_selected_data
    if selected_aggregate_data.empty:
        selected_aggregate_data = data
    else:
        selected_aggregate_data = pd.merge(selected_aggregate_data, data, on='Parameter', how='outer')

# Display the merged data of the selected options
with st.container(border=True):
    st.title('Analysis of Selected Options')
    st.dataframe(selected_aggregate_data.set_index('Parameter'))




# Initialize an empty DataFrame to store the merged data of the selected options
selected_monthly_data = pd.DataFrame()
# Loop through the selected options from monthly_data
for option in selected_options:
    # Check if the option is in monthly_data
    if option in monthly_data.columns:
        # Extract the 'Date' and the selected option columns from the data
        data = monthly_data[['Date', option]]

        # Merge the data with selected_monthly_data
        if selected_monthly_data.empty:
            selected_monthly_data = data
        else:
            selected_monthly_data = pd.merge(selected_monthly_data, data, on='Date', how='outer')


# Display the merged data of the selected options
with st.container(border=True):
    selected_monthly_data['Date'] = pd.to_datetime(selected_monthly_data['Date'])

    # Loop through the columns in selected_monthly_data
    for column in selected_monthly_data.columns:
        # Skip the 'Date' column
        if column != 'Date':
            # Convert the column to float type
            # Replace 'NRF' with 0 in the column
            selected_monthly_data[column] = selected_monthly_data[column].replace('NRF', 0)
            selected_monthly_data.fillna(method='ffill', inplace=True)
            selected_monthly_data[column] = selected_monthly_data[column].apply(
                lambda x: float(x) if isinstance(x, str)  else x)

    with st.container(border=True):
        date_range = st.date_input('Select Date Range', [selected_monthly_data['Date'].min(), selected_monthly_data['Date'].max()], min_value=selected_monthly_data['Date'].min(), max_value=selected_monthly_data['Date'].max())
        selected_monthly_data = selected_monthly_data[(selected_monthly_data['Date'].dt.date >= date_range[0]) & (selected_monthly_data['Date'].dt.date <= date_range[1])]

    with st.container(border=True):
        st.title('Cumulative Performance')

        selected_monthly_data.set_index('Date', inplace=True)
        # Sort the DataFrame by the 'Date' index
        selected_monthly_data.sort_index(inplace=True)

        # Calculate the cumulative sum of each selected option over time
        cumulative_data = selected_monthly_data.cumsum()
        for option in selected_options:
            if option in cumulative_data.columns:
                cumulative_data[option] = pd.to_numeric(cumulative_data[option], errors='coerce')
        # Plot the cumulative sum data
        st.line_chart(cumulative_data, use_container_width=True)

        with st.expander('Show Cumulative Performance Data'):
            st.dataframe(cumulative_data.transpose().iloc[:, -1])
    with st.container(border=True):
        st.title('Analysis of Selected Options')
        st.dataframe(selected_monthly_data)
