import datetime
import os

import pandas as pd

from config import Config
from datapack import Datapack


# Function to gather, filter & join specified census files
def accumulate_census(
    target_folder_path,  # Where the census folder is
    config_path,  # Where the config folder is saved
    geo_type,  # What spatial aggregation sub-folder to target
    output_mode="all",  # Select the output mode,  'merge', 'pivot' or 'all'
    output_folder="",  # Set the location of the output folder, will be the script location by default
    col_desc="short",  # Can be 'short' or 'long'
    col_affix="prefix",
):  # Affix a 'prefix', 'suffix' or 'none' of the csv's file code to each col
    # Set the output folder to be a sub-folder of the script folder if unchanged
    if output_folder == "":
        output_folder = os.path.dirname(os.path.abspath(__file__))

    config = Config(config_path)
    datapack = Datapack(target_folder_path, geo_type, config)

    # List to store column, name
    col_details = []

    # Looping through the per-file-code dictionaries, reading and filtering the resulting dataframes per the config
    for file_details in datapack.details:
        # Prepare the dataframe
        file_path = file_details["full_path"]
        unfiltered_df = pd.read_csv(file_path)
        file_details["unfiltered_df"] = unfiltered_df

        # Grab the current file code
        file_code = file_details["nameparts"]["file_code"]

        # Get the config, and select the rows that match the current file code
        # Save the df as a list of lists, where each list the values in the row
        df = config.df
        df = df[df["DATA_FILE_CODE"] == file_code]
        df = df.drop(columns=["DATA_FILE_CODE"])
        config_rows = df.values.tolist()

        # Dictorary to store the old and new column names before renaming
        col_name_dict = {}

        # Looping over the list of config rows
        # Prepares a dictionary mainly used to create new column names depending on conditions
        for row in config_rows:
            # Getting variables from list
            old_col_name = row[0]  # FIELD_SHORT
            new_col_name = row[1]  # FIELD_LONG
            value_desc = row[2]  # VALUE_DESC
            col_group = row[3]  # GROUP

            # Setting the replacement column name conditionally depending on arguments
            if col_desc == "short":
                new_col_name = old_col_name
            elif col_desc == "long":
                new_col_name = new_col_name
            else:
                print(
                    "col_desc must be either 'short or 'long' - incorrect value entered. Reverting to short."
                )
                new_col_name = old_col_name

            # Adding a prefix or suffix depending on arguments
            if col_affix == "prefix":
                new_col_name = (
                    file_details["nameparts"]["file_code"] + "_" + new_col_name
                )
            elif col_affix == "suffix":
                new_col_name = (
                    new_col_name + "_" + file_details["nameparts"]["file_code"]
                )
            elif col_affix == "none":
                # Leave var unchanged
                new_col_name = new_col_name
            else:
                print(
                    "col_desc must be 'prefix', 'suffix' or 'none' - incorrect value entered. Reverting to none."
                )

            # Adding the old and new key combination to the outer dictionary
            col_name_dict[old_col_name] = new_col_name

            # Adding all column group dictionary to the associated list
            # Creating the dictionary
            col_detail = {
                "old_col": old_col_name,
                "new_col": new_col_name,
                "group": col_group,
                "value_desc": value_desc,
            }

            # Appending that to the list
            col_details.append(col_detail)

        # Getting a list with just the old col names (which are the keys)
        old_col_list = list(col_name_dict.keys())

        # Appending the target columns to the dictionary
        file_details["target_columns"] = col_name_dict

        # Establishing the name of the primary key column
        primary_key_col = str(geo_type) + "_CODE_2021"

        # Adding that to the list of old columns which is used to filter below
        old_col_list.insert(0, primary_key_col)

        # Renaming and filtering columns using the config data
        prepared_df = unfiltered_df.loc[:, old_col_list].rename(columns=col_name_dict)

        # Saving the prepared_df df to the file_details dict, which is in turn saved inplace to datapack.details
        file_details["prepared_df"] = prepared_df

    # # Adding the filtered dataframes to a list
    prepared_dfs = [detail["prepared_df"] for detail in datapack.details]

    # -----------------
    # Merge Output Prep
    # -----------------

    # Merging the dataframes together
    # Create an empty dataframe to store the merged data
    merged_df = pd.DataFrame()

    # Loop through each dataframe in the list and merge with the 'merged_df'
    for df in prepared_dfs:
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = pd.merge(
                merged_df, df, on=primary_key_col, validate="one_to_one"
            )

    # -----------------
    # Pivot Concat Output Prep
    # -----------------

    # Reworking the dictionary containing group and column information
    # Defining the new structure as a dict of lists like {'group': ['col1', 'col2', 'col3'],...}
    group_dict = {}

    for col_detail in col_details:
        group_key = col_detail["group"]
        new_col_value = col_detail["new_col"]
        if group_key not in group_dict:
            group_dict[group_key] = []
        if new_col_value not in group_dict[group_key]:
            group_dict[group_key].append(new_col_value)

    # ---------------------
    # Pivot mode output ETL
    # ---------------------

    # Defining a list to contain output dataframes, which will be used to concat
    pivoted_dfs_list = []

    # Looping over the dictionary to subset, unpivot and create the new 'pivot' dataframes
    for (
        key_group,
        value_col_list,
    ) in (
        group_dict.copy().items()
    ):  # To avoid runtime errors to adding to a dict which being looped over
        # Creating a new list that includes the id column
        group_columns = value_col_list
        group_columns.append(primary_key_col)

        # Create a subset of the merged dataframe containing only columns from the group
        new_df = merged_df[group_columns]

        # Creating a basic dictionary with the old (key) and new names (value)
        value_desc_dict = {}

        for ref_dict in col_details:
            value_desc_dict[f"{ref_dict['new_col']}"] = ref_dict["value_desc"]

        # Using that dictionary to rename columns
        new_df = new_df.rename(columns=value_desc_dict)

        # Getting all columns that are not the primary key column for the pivoting function
        cols_to_unpivot = new_df.columns.difference([primary_key_col])

        # Unpivot dataframe
        new_df_unpivoted = new_df.melt(
            id_vars=[primary_key_col],
            value_vars=cols_to_unpivot,
            var_name=key_group,
            value_name=f"{key_group} Value",
        )

        # Appending those dataframes to the results list
        pivoted_dfs_list.append(new_df_unpivoted)

    # Concat-ing all unpivoted dfs
    pivot_concat_df = pd.concat(pivoted_dfs_list)

    # -----------
    # Creating File names
    # -----------

    # Create file names
    current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")

    # Defining the end part
    end_part = (
        "-" + geo_type + "_" + col_desc + "_" + col_affix + "-" + current_dt + ".csv"
    )

    # File name for the merge output type
    merge_output_fn = "Census Data - Merge" + end_part

    # File name for the pivot concat output type
    pivot_concat_output_fn = "Census Data - Pivot" + end_part

    # Conditionally Output the csv
    if output_mode == "merge":
        merged_df.to_csv(os.path.join(output_folder, merge_output_fn), index=False)
    elif output_mode == "pivot":
        pivot_concat_df.to_csv(
            os.path.join(output_folder, pivot_concat_output_fn), index=False
        )
    elif output_mode == "all":
        merged_df.to_csv(os.path.join(output_folder, merge_output_fn), index=False)
        pivot_concat_df.to_csv(
            os.path.join(output_folder, pivot_concat_output_fn), index=False
        )
    else:
        print(
            "output_mode must be 'merge', 'pivot' or 'all' - wrong value entered. Reverting to merge output"
        )
        merged_df.to_csv(os.path.join(output_folder, merge_output_fn), index=False)


if __name__ == "__main__":
    # Test code

    # Target folder path
    census_folder_path = r"E:/Data/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS"

    # Config file location
    config_file = r"censuswrangler/config_template.csv"

    # Calling the function
    accumulate_census(
        target_folder_path=census_folder_path,
        config_path=config_file,
        geo_type="LGA",
        output_mode="all",
        col_desc="long",
        col_affix="prefix",
    )
