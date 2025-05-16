import pandas as pd

# File paths (adjust as needed)
code_frequency_path = "/mnt/data/code_frequency.csv"  # user-provided CSV file
theme_mapping_path = "/mnt/data/code_theme_mapping.xlsx"  # user-provided Excel file

# Load the data
code_freq_df = pd.read_csv(code_frequency_path)
theme_df = pd.read_excel(theme_mapping_path)

# Merge the two datasets on 'Code', keeping all rows from the frequency data
merged_df = pd.merge(code_freq_df, theme_df, on='Code', how='left')

# Show the result
import ace_tools as tools; tools.display_dataframe_to_user(name="Merged Code Frequency with Themes", dataframe=merged_df)
