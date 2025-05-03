"""Defines the Data class, used for for working with and accessing the census datapack folder."""

import os

from icecream import ic

from censuswrangler.config import Config


class Data:
    """Class for accessing selections of the data inside a datapack. Prepares needed reference info per the details in the provided Config object."""

    def __init__(self, folder_path: str, geo_type: str, config: Config):
        """Initialises the Data class.

        Args:
            folder_path (str): The path of the data folder inside the datapack.
            geo_type (str): The geo type to access e.g. (LGA, SA1, SA2, etc).
            config (Config): The Config object containing config information.
        """
        self.folder_path = folder_path

        # Build a dictionary containing information of the files in the census datapack folder
        # Each entry represents a file code / file
        datapack_details = []
        for root, directories, files in os.walk(folder_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                # Split the filename into its name and type components
                name, file_type = os.path.splitext(filename)
                # Split the name by '_'
                name_parts = name.split("_")
                # Split the path into its components
                path_parts = os.path.split(file_path)
                # Create a dictionary with the path components as key-value pairs
                file_dict = {
                    "filename": name,
                    "nameparts": {
                        "census_desc": name_parts[0],
                        "file_code": name_parts[1],
                        "country": name_parts[2],
                        "geo_type": name_parts[3],
                    },
                    "filetype": file_type,
                    "directory": path_parts[0],
                    "full_path": file_path,
                }
                # Add the dictionary to the list
                datapack_details.append(file_dict)
                # Filter the list to only include the target geo_type and data file codes
                datapack_details = [
                    file_info_dict
                    for file_info_dict in datapack_details
                    if (
                        file_info_dict["nameparts"]["geo_type"] == geo_type
                        and file_info_dict["nameparts"]["file_code"]
                        in config.unique_datapackfile
                        and file_info_dict["filetype"] == ".csv"
                    )
                ]
        self.details = datapack_details

    def summary(self):
        """Prints a summary of the datapack selection"""
        ic(datapack.details)


if __name__ == "__main__":
    folder_path = r"E:/Data/2021_GCP_all_for_AUS_short-header/2021 Census GCP All Geographies for AUS"
    config = Config("censuswrangler/config_template.csv")
    datapack = Data(folder_path, "LGA", config)
    datapack.summary()
