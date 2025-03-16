import pandas as pd
from icecream import ic

# Read the Excel file without specifying the header
excel_file_path = r"E:/Data/2021_GCP_all_for_AUS_short-header/Metadata/Metadata_2021_GCP_DataPack_R1_R2.xlsx"
sheet_names = pd.ExcelFile(excel_file_path, engine="openpyxl").sheet_names


# Find the sheet name that contains any combination of "cell" and "descriptors"
def contains_cell_and_descriptors_in_sheet_name(sheet_name):
    return "cell" in sheet_name.lower() and "descriptors" in sheet_name.lower()


sheet_name = next(
    (name for name in sheet_names if contains_cell_and_descriptors_in_sheet_name(name)),
    None,
)

if sheet_name is None:
    raise ValueError("No sheet name contains 'cell' and 'descriptors'.")

# Read the Excel file with the detected sheet name
metadata_df = pd.read_excel(
    excel_file_path,
    sheet_name=sheet_name,
    engine="openpyxl",
    header=None,
)


# Define a function to check if a row contains "Cell" and "Descriptors"
def contains_cell_and_descriptors(row):
    contains_cell = row.astype(str).str.contains("Cell", case=False).any()
    contains_descriptors = row.astype(str).str.contains("Descriptors", case=False).any()
    return contains_cell and contains_descriptors


# Find the row where "Cell" and "Descriptors" appear
header_row_index = metadata_df.apply(contains_cell_and_descriptors, axis=1).idxmax()

# Use the row after the found row as the header with values in lower case, and strip spaces
metadata_df.columns = metadata_df.iloc[header_row_index + 1].str.lower()
metadata_df.columns = metadata_df.columns.str.strip()

# Drop the rows up to and including the header row
metadata_df = metadata_df.drop(index=range(header_row_index + 2))

# Reset the index of the DataFrame
metadata_df = metadata_df.reset_index(drop=True)
metadata_df.index = metadata_df.index + 1

# Start a dict with a key for each column containing a list of its unique values
metadata_info = {col: metadata_df[col].unique().tolist() for col in metadata_df.columns}

metadata_info["df"] = metadata_df

ic(metadata_info["df"])
