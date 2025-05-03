"""Module for working with the config file."""

import os
import shutil

from icecream import ic
import pandas as pd

from censuswrangler._schemas import config_schema


class Config:
    """Class for accessing the config file, providing useful attributes and checking the validity of the configuration."""

    def __init__(self, config_path: str):
        """Initialises the Config class object.

        Args:
            config_path (str): The file path of the config csv.
        """
        # Check if the config file exists then read it into a DataFrame
        self.config_path: str = config_path
        self.config_path_abs: str = os.path.abspath(config_path)
        assert os.path.exists(config_path), f"Config file not found at: {config_path}"
        self.df: pd.DataFrame = config_schema(pd.read_csv(config_path))

        # Cast all columns as strings
        self.df = self.df.astype(str)

        # Count rows
        self.row_count: int = len(self.df)
        self.unique_row_count: int = len(self.df.drop_duplicates())

        # Assert that there are no duplicate rows
        if self.row_count != self.unique_row_count:
            print("Duplicate rows found in config file, these will be ignored")

        # Get unique values for each column
        self.unique_datapackfile: list = self.df["DATAPACKFILE"].unique().tolist()
        self.unique_datapackfile_count: int = len(self.unique_datapackfile)

        self.unique_short: list = self.df["SHORT"].unique().tolist()
        self.unique_short_count: int = len(self.unique_short)

        self.unique_long: list = self.df["LONG"].unique().tolist()
        self.unique_long_count: int = len(self.unique_long)

        self.unique_custom_description: list = (
            self.df["CUSTOM_DESCRIPTION"].unique().tolist()
        )
        self.unique_custom_description_count: int = len(self.unique_custom_description)

        self.unique_custom_group: list = self.df["CUSTOM_GROUP"].unique().tolist()
        self.unique_custom_group_count: int = len(self.unique_custom_group)

    def summary(self):
        """Prints a summary of the config file"""
        ln = "-" * 50
        print(ln)
        print("Config file summary")
        print(ln)
        ic(self.config_path)
        ic(self.config_path_abs)
        ic(self.row_count)
        ic(self.unique_row_count)
        print(ln)
        ic(self.unique_datapackfile_count)
        ic(self.unique_short_count)
        ic(self.unique_long_count)
        ic(self.unique_custom_description_count)
        ic(self.unique_custom_group_count)
        print(ln)
        ic(self.unique_datapackfile)
        ic(self.unique_short)
        ic(self.unique_long)
        ic(self.unique_custom_description)
        ic(self.unique_custom_group)
        print(ln)


def create_config_template(
    output_folder: str, file_name: str = "censuswrangler_config"
) -> None:
    """Create a template config csv for use with the census

    Args:
        output_folder (str): The folder path where the config file will be created.
        file_name (str, optional): The name of the config file, excluding file type. Defaults to "censuswrangler_config".
    """
    assert os.path.isdir(output_folder), (
        f"The provided folder_path argument '{output_folder}' is not a directory or does not exist."
    )
    template_source = "censuswrangler/config_template.csv"
    output_path = os.path.join(output_folder, file_name + ".csv")
    output_path_abs = os.path.abspath(output_path)
    assert not os.path.exists(output_path), (
        f"File '{output_path_abs}' already exists, file creation aborted."
    )
    shutil.copy(template_source, output_path)
    print(f"Successfully created censuswrangler config template: '{output_path_abs}'")


if __name__ == "__main__":
    from icecream import ic

    # # Example usage with the config template
    # config = Config("censuswrangler/config_template.csv")
    # config.summary()
    create_config_template("test_output")
