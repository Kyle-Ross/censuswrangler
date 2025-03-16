import os
import re

import pandas as pd

from _schemas import metadata_schema


def pack(
    folder_path: str,
    must_haves: list = ["Metadata", "Readme"],
    expectation_description: str = "Census Datapack folder",
    expected_folders: int = 3,
) -> dict[dict]:
    """Grabs a datapack path and builds a nested dictionary with info on each folder within. Checks against expectations."""

    def _check_dir(path: str) -> None:
        """Check that a string is a directory path."""
        assert os.path.isdir(path), f"Error: '{path}' is not a directory."

    # Check the provided path
    _check_dir(folder_path)

    # Grab folder names and check them over
    folder_names = os.listdir(folder_path)
    folder_names_lower = [x.lower() for x in folder_names]
    folder_names_count = len(folder_names)
    # Run checks
    assert folder_names_count == expected_folders, (
        f"Expected '{folder_path}' to have {expected_folders} folders. Instead it has {folder_names_count}, please review. Description: {expectation_description}"
    )
    assert all(item.lower() in folder_names_lower for item in must_haves), (
        f"Required folders '{must_haves}' must all exist in folder '{folder_path}'"
    )

    # Gather info on each folder, build dict for each
    folder_info = {}
    for name in folder_names:
        # Get the full path
        path = os.path.join(folder_path, name)
        _check_dir(path)

        # Build the nested dict
        info = {}
        info["name"] = name
        info["path"] = path

        # Categorise the folder by type
        name_lower = name.lower()
        folder_type = ""
        if name_lower in ("metadata", "readme"):
            folder_type = name_lower
        else:
            folder_type = "data"

        # Add that to the outer dict by type
        folder_info[folder_type] = info

    # ----------------------------------------------
    # Build details on the files in the meta data folder
    # ----------------------------------------------

    # Initialise dict to contain info on the files of the metadata folder
    folder_info["metadata"]["files"] = {}

    # Loop through the metadata files and add them to that dict
    for root, dirs, files in os.walk(folder_info["metadata"]["path"]):
        for file_name_and_ext in files:
            # Split that out
            parts: tuple = os.path.splitext(file_name_and_ext)
            name: str = parts[0]
            ext: str = parts[1]
            path = os.path.join(root, name + ext)

            def assert_type(ext: str, expected_ext: str, file_desc: str):
                """Check that that an extension is what was expected"""
                assert ext.lower() == expected_ext, (
                    f"Expected '{file_desc}' to be file type '{expected_ext}, instead got type '{ext}'"
                )

            # Identify the files, check their types
            file_desc = ""
            if bool(re.match(r"^Metadata_", name)):
                desc = "metadata"
                assert_type(ext, ".xlsx", desc)
                file_desc = desc
            elif bool(re.search(r"_Sequential_Template_", name)):
                desc = "sequential_template"
                assert_type(ext, ".xlsx", desc)
                file_desc = desc
            elif bool(re.search(r"_geog_desc_", name)):
                desc = "geographic_descriptions"
                assert_type(ext, ".xlsx", desc)
                file_desc = desc
            else:
                file_desc = name

            # Build a file details dict and put it into the pack dictionary
            file_info = {}
            file_info["name"] = name
            file_info["ext"] = ext
            file_info["path"] = path

            folder_info["metadata"]["files"][file_desc] = file_info

    # ----------------------------------------------
    # Extract the information in the cell descriptors sheet of the metadata xlsx
    # ----------------------------------------------

    # Read the Excel file without specifying the header
    metadata_file_path = folder_info["metadata"]["files"]["metadata"]["path"]
    sheet_names = pd.ExcelFile(metadata_file_path, engine="openpyxl").sheet_names

    # Find the sheet name that contains any combination of "cell" and "descriptors"
    def contains_cell_and_descriptors_in_sheet_name(sheet_name):
        return "cell" in sheet_name.lower() and "descriptors" in sheet_name.lower()

    sheet_name = next(
        (
            name
            for name in sheet_names
            if contains_cell_and_descriptors_in_sheet_name(name)
        ),
        None,
    )

    if sheet_name is None:
        raise ValueError(
            "No sheet name in the metadata xlsx contains 'cell' and 'descriptors'."
        )

    # Read the Excel file with the detected sheet name
    metadata_df = pd.read_excel(
        metadata_file_path,
        sheet_name=sheet_name,
        engine="openpyxl",
        header=None,
    )

    # Define a function to check if a row contains "Cell" and "Descriptors"
    def contains_cell_and_descriptors(row):
        contains_cell = row.astype(str).str.contains("Cell", case=False).any()
        contains_descriptors = (
            row.astype(str).str.contains("Descriptors", case=False).any()
        )
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

    # Validate the metadata df
    validated_metadata_df = metadata_schema(metadata_df)

    # Start a dict with a key for each column containing a list of its unique values
    metadata_column_uniques = {
        col: metadata_df[col].unique().tolist() for col in metadata_df.columns
    }

    # Pack that up into its own dict, with the df
    metadata_info = {}
    metadata_info["df"] = validated_metadata_df
    metadata_info["columns"] = metadata_column_uniques

    # Add those to the dictionary
    folder_info["metadata"]["files"]["metadata"].update(metadata_info)

    return folder_info


if __name__ == "__main__":
    path = r"E:/Data/2021_GCP_all_for_AUS_short-header/"
    pack = pack(path)

    def print_dict_keys(d, indent=0):
        """Visualise the dictionary structure"""
        for key, value in d.items():
            print(" " * indent + str(key) + ":")
            if isinstance(value, dict):
                print_dict_keys(value, indent + 4)
            else:
                print(" " * (indent + 4) + "...")

    print_dict_keys(pack)
