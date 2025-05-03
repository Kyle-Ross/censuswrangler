"""
The census module provides the Census class, which encapsulates common configuration and datapack objects,
and provides methods to gather, filter, join, and output census data based on specified configurations.
"""

from typing import Dict, Optional
import copy
import datetime
import os

import pandas as pd

from censuswrangler._pack import pack
from censuswrangler._data import Data
from censuswrangler.config import Config


class Census:
    """
    The `Census` class is designed to facilitate the processing and manipulation of census data.
    It integrates configuration and datapack objects, enabling users to gather, filter, join,
    and output census data based on specified configurations. The class supports operations
    such as merging and pivoting dataframes, and provides methods to validate and output the
    processed data.

    Attributes:
        datapack_path (str): Path to the folder containing the census datapack.
        config_path (str): Path to the configuration file.
        geo_type (str): The spatial aggregation sub-folder to target (e.g., LGA, SA2).
        year (int): The census year used to identify columns in the datapack.
        col_type (str): The type of column output to use, either 'short' or 'long'. Defaults to 'short'.
        affix_type (str): Specifies whether to add a 'prefix', 'suffix', or 'none' to column names. Defaults to 'prefix'.
        config (Config): An instance of the `Config` class, representing the configuration file.
        pack (dict): A dictionary containing all the information needed to work on the datapack.
        data (Data): An instance of the `Data` class, built from the target geo and configuration.
        merged_df (Optional[pd.DataFrame]): A dataframe to store merged data after the `wrangle` method is called.
        pivoted_df (Optional[pd.DataFrame]): A dataframe to store pivoted data after the `wrangle` method is called.
    """

    def __init__(
        self,
        datapack_path: str,
        config_path: str,
        geo_type: str,
        year: int,
        col_type: str = "short",
        affix_type: str = "prefix",
    ):
        """
        Initializes the `Census` class with the specified datapack and configuration paths,
        geographic type, year, column type, and affix type. It also validates input parameters
        and prepares the necessary objects for data processing.

        Args:
            datapack_path (str): Path to the folder containing the census datapack.
            config_path (str): Path to the configuration file.
            geo_type (str): The spatial aggregation sub-folder to target (e.g., LGA, SA2).
            year (int): The census year used to identify columns in the datapack.
            col_type (str, optional): The type of column output to use, either 'short' or 'long'. Defaults to 'short'.
            affix_type (str, optional): Specifies whether to add a 'prefix', 'suffix', or 'none' to column names. Defaults to 'prefix'.

        Raises:
            AssertionError: If `col_type` is not one of the allowed values ('short', 'long').
            AssertionError: If `affix_type` is not one of the allowed values ('prefix', 'suffix', 'none').
        """
        # Where the census folder is
        self.datapack_path: str = datapack_path
        # Where the config file is saved
        self.config_path: str = config_path
        # What spatial aggregation sub-folder to target
        self.geo_type: str = geo_type
        # Helps find columns in the datapack, which have the census year as a suffix
        self.year: int = year
        # The type of column output to use. Can be 'short' or 'long'
        self.col_type: str = col_type
        # Affix a 'prefix', 'suffix' or 'none' of the csv's file code to each col, and put arg on file name
        self.affix_type: str = affix_type
        # Config object
        self.config: Config = Config(config_path)
        # All the info needed to work on the datapack
        self.pack: dict = pack(datapack_path)
        # Data object built from the target geo and config
        self.data: Data = Data(self.pack["data"]["path"], geo_type, self.config)
        # Allowed values for the output argument
        self._allowed_output_modes: Dict[Dict] = {
            "merge": {
                "requirement": "First run the Census.wrangle method with mode = 'merge'"
            },
            "pivot": {
                "requirement": "First run the Census.wrangle method with mode = 'pivot'"
            },
            "all": {
                "requirement": "First run the Census.wrangle method with mode = 'all'"
            },
        }

        # Basic parameter assertions
        allowed_col_types = ("short", "long")
        assert col_type in allowed_col_types, (
            f"col_type argument '{col_type} not in allowed types {allowed_col_types}"
        )

        allowed_affix_types = ("prefix", "suffix", "none")
        assert affix_type in allowed_affix_types, (
            f"affix_type argument '{affix_type} not in allowed types {allowed_affix_types}"
        )

        # Asserting that relevant config values exist in the metadata file of the pack
        def _assert_valid_metadata(config_list: list, metadata_col: str):
            """Common function for config metadata validation"""
            valid_entries = self.pack["metadata"]["files"]["metadata"]["columns"][
                metadata_col
            ]
            for entry in config_list:
                assert entry in valid_entries, (
                    f"'{entry}' in config file '{self.config.config_path_abs}' is not valid per datapack metadata in '{self.pack['metadata']['files']['metadata']['path']}', see sheet - 'Cell Descriptions Information'"
                )

        # Asserting each of the relevant config columns are valid
        _assert_valid_metadata(self.config.unique_short, "short")
        _assert_valid_metadata(self.config.unique_long, "long")
        _assert_valid_metadata(self.config.unique_datapackfile, "datapackfile")

        # Dataframes to store the merged and pivoted data (once wrangle is called)
        self.merged_df: Optional[pd.DataFrame] = None
        self.pivoted_df: Optional[pd.DataFrame] = None

    def _assert_mode_arg(self, mode):
        """Internal function to check the mode is in the allowed values"""
        allowed = self._allowed_output_modes.keys()
        assert mode in allowed, (
            f"mode argument '{mode}' not in allowed modes '{allowed}'"
        )

    def wrangle(self, mode):
        """
        Processes census data by gathering, filtering, and joining specified census files
        based on the configuration and datapack objects in the Census class.

        This method performs the following steps:

        1. Validates the `mode` argument to ensure it is one of the allowed values ('merge', 'pivot', 'all').
        2. Reads and filters data from census files based on the configuration.
        3. Renames and prepares columns according to the specified column type (`col_type`) and affix type (`affix_type`).
        4. Merges the prepared dataframes if the mode is 'merge' or 'all'.
        5. Creates pivoted dataframes grouped by specified column groups if the mode is 'pivot' or 'all'.

        Args:
            mode (str): The processing mode, which determines the type of operation to perform ('merge', 'pivot', 'all').

        Raises:
            AssertionError: If the `mode` argument is not one of the allowed values.
            ValueError: If invalid values are provided for `col_type` or `affix_type`.
        """
        self._assert_mode_arg(mode)

        # ===========
        # Prepare target dataframes
        # ===========

        # List to store column, name
        col_details = []

        # Looping through the per-file-code dictionaries, reading and filtering the resulting dataframes per the config
        for file_details in self.data.details:
            # Prepare the dataframe
            file_path = file_details["full_path"]
            unfiltered_df = pd.read_csv(file_path)
            file_details["unfiltered_df"] = unfiltered_df

            # Grab the current file code
            file_code = file_details["nameparts"]["file_code"]

            # Get the config, and select the rows that match the current file code
            # Save the df as a list of lists, where each list the values in the row
            df = self.config.df
            df = df[df["DATAPACKFILE"] == file_code]
            df = df.drop(columns=["DATAPACKFILE"])
            config_rows = df.values.tolist()

            # Store the column order
            short_index: int = df.columns.get_loc("SHORT")
            long_index: int = df.columns.get_loc("LONG")
            custom_description_index: int = df.columns.get_loc("CUSTOM_DESCRIPTION")
            custom_group_index: int = df.columns.get_loc("CUSTOM_GROUP")

            # Dictorary to store the old and new column names before renaming
            col_name_dict = {}

            # Looping over the list of config rows
            # Prepares a dictionary mainly used to create new column names depending on conditions
            for row in config_rows:
                # Getting variables from list
                col_short = row[short_index]  # SHORT
                col_name = row[long_index]  # LONG
                col_desc = row[custom_description_index]  # CUSTOM_DESCRIPTION
                col_group = row[custom_group_index]  # CUSTOM_GROUP

                # Setting the replacement column name conditionally depending on arguments
                if self.col_type == "short":
                    col_name = col_short
                elif self.col_type == "long":
                    col_name = col_name
                else:
                    raise ValueError(
                        "col_type must be either 'short or 'long' - incorrect value entered."
                    )

                # Adding a prefix or suffix depending on arguments
                if self.affix_type == "prefix":
                    col_name = file_details["nameparts"]["file_code"] + "_" + col_name
                elif self.affix_type == "suffix":
                    col_name = col_name + "_" + file_details["nameparts"]["file_code"]
                elif self.affix_type == "none":
                    # Leave var unchanged
                    col_name = col_name
                else:
                    raise ValueError(
                        "affix_type must be 'prefix', 'suffix' or 'none' - incorrect value entered."
                    )

                # Adding the old and new key combination to the outer dictionary
                col_name_dict[col_short] = col_name

                # Adding all column group dictionary to the associated list
                # Creating the dictionary
                col_detail = {
                    "old_col": col_short,
                    "new_col": col_name,
                    "group": col_group,
                    "col_desc": col_desc,
                }

                # Appending that to the list
                col_details.append(col_detail)

            # Getting a list with just the old col names (which are the keys)
            old_col_list = list(col_name_dict.keys())

            # Appending the target columns to the dictionary
            file_details["target_columns"] = col_name_dict

            # Establishing the name of the primary key column
            # This is basically the geocode with a suffix
            primary_key_col = f"{self.geo_type}_CODE_{self.year}"

            # Adding that to the list of old columns which is used to filter below
            old_col_list.insert(0, primary_key_col)

            # Renaming and filtering columns using the config data
            prepared_df = unfiltered_df.loc[:, old_col_list].rename(
                columns=col_name_dict
            )

            # Saving the prepared_df df to the file_details dict, which is in turn saved inplace to datapack.details
            file_details["prepared_df"] = prepared_df

        # ===========
        # Preparing outputs
        # ===========

        # ------------
        # Merge mode
        # ------------
        # Create an empty dataframe to store the merged data
        # Used in the pivot mode as well
        if mode == "merge" or mode == "pivot" or mode == "all":
            # Get all prepared dataframes in a list
            prepared_dfs = [detail["prepared_df"] for detail in self.data.details]

            # Loop through each dataframe in the list and merge with the 'merged_df'
            # Use the first df as the base and merge the rest on the primary key column
            for df in prepared_dfs:
                if self.merged_df is None:
                    self.merged_df = df
                else:
                    self.merged_df = pd.merge(
                        self.merged_df, df, on=primary_key_col, validate="one_to_one"
                    )

        # ------------
        # Pivot mode
        # ------------
        if mode == "pivot" or mode == "all":
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
                new_df = copy.deepcopy(self.merged_df[group_columns])

                # Creating a basic dictionary with the old (key) and new names (value)
                col_desc_dict = {}

                for ref_dict in col_details:
                    col_desc_dict[f"{ref_dict['new_col']}"] = ref_dict["col_desc"]

                # Using that dictionary to rename columns
                new_df = new_df.rename(columns=col_desc_dict)

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

            # Assign it to the class attribute
            self.pivoted_df = pivot_concat_df

    def to_csv(self, mode: str, output_folder: str):
        """
        Outputs the processed census data to CSV files in the specified output folder.

        This method generates CSV files based on the specified mode ('merge', 'pivot', or 'all')
        and saves them to the provided output folder. The filenames include metadata such as
        geographic type, column type, affix type, and the current timestamp.

        Args:
            mode (str): The output mode, which determines the type of data to export ('merge', 'pivot', 'all').
            output_folder (str): The directory where the CSV files will be saved. Must be an existing directory.

        Raises:
            AssertionError: If the specified `output_folder` does not exist or is not a directory.
            ValueError: If the `mode` argument is not one of the allowed values ('merge', 'pivot', 'all').
        """

        self._assert_mode_arg(mode)

        # Check the folder directory
        assert os.path.isdir(output_folder), (
            f"The path '{output_folder}' is not a directory or does not exist."
        )

        # Common file name elements
        current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
        file_name_end = (
            "-"
            + self.geo_type
            + "_"
            + self.col_type
            + "_"
            + self.affix_type
            + "-"
            + current_dt
            + ".csv"
        )

        # Set names for the output types
        merge_name = "Census Data - Merge" + file_name_end
        pivot_name = "Census Data - Pivot" + file_name_end

        # Common csv output function
        def df_to_csv(df, name, index=False):
            df.to_csv(os.path.join(output_folder, name), index=index)

        # Conditionally Output the csv
        if mode == "merge":
            df_to_csv(self.merged_df, merge_name)
        elif mode == "pivot":
            df_to_csv(self.pivoted_df, pivot_name)
        elif mode == "all":
            df_to_csv(self.merged_df, merge_name)
            df_to_csv(self.pivoted_df, pivot_name)
        else:
            raise ValueError(
                f"'{mode}' is invalid. mode must be one of allowed values {self._allowed_output_modes.keys()}"
            )


if __name__ == "__main__":
    from icecream import ic

    census = Census(
        datapack_path=r"E:/Data/2021_GCP_all_for_AUS_short-header/",
        config_path=r"censuswrangler/config_template.csv",
        geo_type="LGA",
        year=2021,
    )

    census.wrangle("all")
    ic(census.merged_df.head(3))
    census.to_csv("all", r"F:/Github/censuswrangler/test_output")
