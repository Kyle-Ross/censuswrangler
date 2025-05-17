"""Module for working with the config file."""

from io import StringIO
import os

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
    output_folder: str = None, file_name: str = "censuswrangler_config"
) -> None:
    """Create a template config csv for use with the census

    Args:
        output_folder (str, optional): The folder path where the config file will be created. Defaults to the script location.
        file_name (str, optional): The name of the config file, excluding file type. Defaults to "censuswrangler_config".
    """
    # Determine is output_folder is blank
    output_folder_is_set = False
    if not (output_folder is None or output_folder == ""):
        output_folder_is_set = True

    # Allow none or blank but check folder if path is provided
    if output_folder_is_set:
        assert os.path.isdir(output_folder), (
            f"The provided folder_path argument '{output_folder}' is not a directory or does not exist."
        )

    # The whole config as a string, then converted into a csv
    csv_source = """SHORT,LONG,DATAPACKFILE,CUSTOM_DESCRIPTION,CUSTOM_GROUP
Tot_P_M,Total_Persons_Males,G01,Male,Gender
Tot_P_F,Total_Persons_Females,G01,Female,Gender
Age_0_4_yr_M,Age_groups_0_4_years_Males,G01,0 - 4 years,Age - Male
Age_0_4_yr_F,Age_groups_0_4_years_Females,G01,0 - 4 years,Age - Female
Age_0_4_yr_P,Age_groups_0_4_years_Persons,G01,0 - 4 years,Age - Person
Age_5_14_yr_M,Age_groups_5_14_years_Males,G01,5 - 14 years,Age - Male
Age_5_14_yr_F,Age_groups_5_14_years_Females,G01,5 - 14 years,Age - Female
Age_5_14_yr_P,Age_groups_5_14_years_Persons,G01,5 - 14 years,Age - Person
Age_15_19_yr_M,Age_groups_15_19_years_Males,G01,15 - 19 years,Age - Male
Age_15_19_yr_F,Age_groups_15_19_years_Females,G01,15 - 19 years,Age - Female
Age_15_19_yr_P,Age_groups_15_19_years_Persons,G01,15 - 19 years,Age - Person
Age_20_24_yr_M,Age_groups_20_24_years_Males,G01,20 - 24 years,Age - Male
Age_20_24_yr_F,Age_groups_20_24_years_Females,G01,20 - 24 years,Age - Female
Age_20_24_yr_P,Age_groups_20_24_years_Persons,G01,20 - 24 years,Age - Person
Age_25_34_yr_M,Age_groups_25_34_years_Males,G01,25 - 34 years,Age - Male
Age_25_34_yr_F,Age_groups_25_34_years_Females,G01,25 - 34 years,Age - Female
Age_25_34_yr_P,Age_groups_25_34_years_Persons,G01,25 - 34 years,Age - Person
Age_35_44_yr_M,Age_groups_35_44_years_Males,G01,35 - 44 years,Age - Male
Age_35_44_yr_F,Age_groups_35_44_years_Females,G01,35 - 44 years,Age - Female
Age_35_44_yr_P,Age_groups_35_44_years_Persons,G01,35 - 44 years,Age - Person
Age_45_54_yr_M,Age_groups_45_54_years_Males,G01,45 - 54 years,Age - Male
Age_45_54_yr_F,Age_groups_45_54_years_Females,G01,45 - 54 years,Age - Female
Age_45_54_yr_P,Age_groups_45_54_years_Persons,G01,45 - 54 years,Age - Person
Age_55_64_yr_M,Age_groups_55_64_years_Males,G01,55 - 64 years,Age - Male
Age_55_64_yr_F,Age_groups_55_64_years_Females,G01,55 - 64 years,Age - Female
Age_55_64_yr_P,Age_groups_55_64_years_Persons,G01,55 - 64 years,Age - Person
Age_65_74_yr_M,Age_groups_65_74_years_Males,G01,65 - 74 years,Age - Male
Age_65_74_yr_F,Age_groups_65_74_years_Females,G01,65 - 74 years,Age - Female
Age_65_74_yr_P,Age_groups_65_74_years_Persons,G01,65 - 74 years,Age - Person
Age_75_84_yr_M,Age_groups_75_84_years_Males,G01,75 - 84 years,Age - Male
Age_75_84_yr_F,Age_groups_75_84_years_Females,G01,75 - 84 years,Age - Female
Age_75_84_yr_P,Age_groups_75_84_years_Persons,G01,75 - 84 years,Age - Person
Age_85ov_M,Age_groups_85_years_and_over_Males,G01,> 85 years,Age - Male
Age_85ov_F,Age_groups_85_years_and_over_Females,G01,> 85 years,Age - Female
Age_85ov_P,Age_groups_85_years_and_over_Persons,G01,> 85 years,Age - Person
P_Tot_Marrd_reg_marrge,PERSONS_Total_Married_in_a_registered_marriage,G06,Married,Relationship Type
P_Tot_Married_de_facto,PERSONS_Total_Married_in_a_de_facto_marriage,G06,Couple,Relationship Type
P_Tot_Not_married,PERSONS_Total_Not_married,G06,No relationship,Relationship Type"""
    csv_df = pd.read_csv(StringIO(csv_source))

    # Prepare the output
    output_path = file_name + ".csv"
    if output_folder_is_set:
        output_path = os.path.join(output_folder, output_path)
    output_path_abs = os.path.abspath(output_path)

    # Check it isn't already there
    assert not os.path.exists(output_path), (
        f"File '{output_path_abs}' already exists, file creation aborted."
    )

    # Create the file and print the success message
    csv_df.to_csv(output_path, index=False)
    print(f"Successfully created censuswrangler config template: '{output_path_abs}'")


if __name__ == "__main__":
    from icecream import ic

    # # Example usage with the config template
    # config = Config("censuswrangler/config_template.csv")
    # config.summary()
    create_config_template("test_output")
