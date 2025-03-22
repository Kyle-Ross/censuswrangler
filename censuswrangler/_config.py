"""Module for working with the config file"""

import os

from icecream import ic
import pandas as pd


class Config:
    """Class for working with the config file"""

    def __init__(self, config_path: str):
        # Check if the config file exists then read it into a DataFrame
        self.config_path: str = config_path
        self.config_path_abs: str = os.path.abspath(config_path)
        assert os.path.exists(config_path), f"Config file not found at: {config_path}"
        self.df: pd.DataFrame = pd.read_csv(config_path)

        # Check if the required columns are present
        _required_columns = [
            "SHORT",
            "LONG",
            "DATAPACKFILE",
            "CUSTOM_DESCRIPTION",
            "CUSTOM_GROUP",
        ]
        for column in _required_columns:
            assert column in self.df.columns, f"Missing required column: {column}"

        # List all columns except data file code
        self._output_columns: list = _required_columns[1:]

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

        self.unique_custom_description: list = self.df["CUSTOM_DESCRIPTION"].unique().tolist()
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


if __name__ == "__main__":
    from icecream import ic

    # Example usage with the config template
    config = Config("censuswrangler/config_template.csv")
    config.summary()
