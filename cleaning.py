import os
import pandas as pd

# Initialize an empty dictionary to hold all DataFrames
dfs = {}

# Walk through all subdirectories in the 'data' directory
for root, dirs, files in os.walk('data'):
    for file in files:
        # Check if the file ends with 'table_1.csv'
        if file.endswith('table_1.csv'):
            # Construct the full file path
            file_path = os.path.join(root, file)
            # Read the file into a DataFrame
            df = pd.read_csv(file_path)
            # Standardize the date column name
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            # Get the option name from the second column name
            option_name = df.columns[1]
            # Add the DataFrame to the dictionary
            dfs[option_name] = df
            df['Date'] = pd.to_datetime(df['Date'], format='mixed')

# Initialize the merged DataFrame as the first DataFrame in the dictionary
merged_df = next(iter(dfs.values()))

# Merge all other DataFrames in the dictionary with the merged DataFrame
for option_name, df in list(dfs.items())[1:]:
    merged_df = pd.merge(merged_df, df, on='Date', how='outer')

# Convert the 'Date' column to datetime format
# merged_df['Date'] = pd.to_datetime(merged_df['Date'], format='mixed')

# Sort the DataFrame by the 'Date' column
merged_df.sort_values('Date', inplace=True)

# Reset the index of the DataFrame
merged_df.reset_index(drop=True, inplace=True)
# Save the merged DataFrame to a new CSV file
merged_df.to_csv('pms_performance_monthly.csv', index=False)