import pandas as pd
import datetime
import json
import os

# Target folder path
census_folder_path = r"C:\Users\rossk\Github\abs-census-merger\2021_GCP_all_for_AUS_short-header\2021 Census GCP All Geographies for AUS"

# Config file location
config_file = r"C:\Users\rossk\Github\abs-census-merger\config.csv"

# Function to pretty print dictionaries
def print_dict(target_dict):
    # Deals with dataframes in the dict
    def if_df_in_dict(obj):
        if isinstance(obj, pd.DataFrame):
            return "DataFrame Object"
        raise TypeError(f"{type(obj)} not supported")

    print(json.dumps(target_dict, default=if_df_in_dict, indent=4))


# Function to get dictionaries containing information on each file in the census folder
def census_file_info(folder_path):
    # Get all file paths in the target folder
    file_paths = []
    for root, directories, files in os.walk(folder_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            # Split the filename into its name and type components
            name, file_type = os.path.splitext(filename)
            # Split the name by '_'
            name_parts = name.split('_')
            # Split the path into its components
            path_parts = os.path.split(file_path)
            # Create a dictionary with the path components as key-value pairs
            file_dict = {
                'filename': name,
                'nameparts':
                    {
                        "census_desc": name_parts[0],
                        "file_code": name_parts[1],
                        "country": name_parts[2],
                        "geo_type": name_parts[3]
                    },
                'filetype': file_type,
                'directory': path_parts[0],
                'full_path': file_path
            }
            # Add the dictionary to the list
            file_paths.append(file_dict)

    # Returning the result
    return file_paths


# Function to gather, filter & join specified census files
def accumulate_census(target_folder_path,  # Where the census folder is
                      config_path,  # Where the config folder is saved
                      geo_type,  # What spatial aggregation sub-folder to target
                      output_folder='',  # Set the location of the output folder, will be the script location by default
                      col_desc='short',  # Can be 'short' or 'long'
                      col_affix='prefix'):  # Affix a 'prefix', 'suffix' or 'none' of the csv's file code to each col
    # Set the output folder to be a sub-folder of the script folder if unchanged
    if output_folder == '':
        output_folder = os.path.dirname(os.path.abspath(__file__))

    # Getting the list of dictionaries with file info
    file_dicts = census_file_info(target_folder_path)

    # Getting config file
    config_data = pd.read_csv(config_path)

    # List of unique data file codes in the config
    distinct_file_codes = config_data['DATA_FILE_CODE'].unique().tolist()

    # Reducing the list to only the target csvs based on the config file
    targeted_file_paths = []

    for file_info_dict in file_dicts:
        file_info_dict['nameparts']['file_code']
        if file_info_dict['nameparts']['geo_type'] == geo_type and \
                file_info_dict['nameparts']['file_code'] in distinct_file_codes and \
                file_info_dict['filetype'] == ".csv":
            targeted_file_paths.append(file_info_dict)

    # Looping through the dictionaries, reading and filtering the resulting dataframes
    for file_dict in targeted_file_paths:
        # Getting the file path
        file_path = file_dict['full_path']

        # Opening the csv as a df
        unfiltered_df = pd.read_csv(file_path)

        # Saving the unfiltered df to the dict
        file_dict["unfiltered_df"] = unfiltered_df

        # Creating a list of column names to keep from the config file, where index 0 is the old name and 1 is the new
        col_list_list = config_data[config_data['DATA_FILE_CODE'] == file_dict['nameparts']['file_code']] \
            [['FIELD_SHORT', 'FIELD_LONG']].drop_duplicates().values.tolist()

        # Looping through col list and putting it in a dictionary
        col_dict = {}

        for cols_list in col_list_list:
            # Getting col names
            old_col_name = cols_list[0]

            # Setting the replacement column name conditionally depending on arguments
            if col_desc == 'short':
                new_col_name = old_col_name
            elif col_desc == 'long':
                new_col_name = cols_list[1]
            else:
                print("col_desc must be either 'short or 'long' - incorrect value entered. Reverting to short.")
                new_col_name = old_col_name

            # Adding a prefix or suffix depending on arguments
            if col_affix == 'prefix':
                new_col_name = file_dict['nameparts']['file_code'] + "_" + new_col_name
            elif col_affix == 'suffix':
                new_col_name = new_col_name + "_" + file_dict['nameparts']['file_code']
            elif col_affix == 'none':
                # Leave var unchanged
                new_col_name = new_col_name
            else:
                print("col_desc must be 'prefix', 'suffix' or 'none' - incorrect value entered. Reverting to none.")
                # Do nothing

            # Adding the old and new key combination to the dictionary
            col_dict[old_col_name] = new_col_name

        # Getting a list with just the old col name
        old_col_list = [x[0] for x in col_list_list]

        # Appending the target columns to the dictionary
        file_dict["target_columns"] = col_dict

        # Establishing the name of the primary key column
        primary_key_col = str(geo_type) + "_CODE_2021"

        # Adding that to the list of old columns which is used to filter below
        old_col_list.insert(0, primary_key_col)

        # Renaming and filtering columns using the config data
        filtered_df = unfiltered_df.loc[:, old_col_list].rename(columns=col_dict)

        # Saving the filtered df to the dict
        file_dict["filtered_df"] = filtered_df

    # Adding the filtered dataframes to a list
    filtered_df_list = []

    for a_dict in targeted_file_paths:
        filtered_df_list.append(a_dict["filtered_df"])

    # Merging the dataframes together
    # Create an empty dataframe to store the merged data
    merged_df = pd.DataFrame()

    # Loop through each dataframe in the list and merge with the 'merged_df'
    for df in filtered_df_list:
        if merged_df.empty:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=primary_key_col, validate='one_to_one')

    # Create file name
    current_dt = datetime.datetime.now().strftime("%Y-%m-%d %H-%M")
    output_file_name = "Census Data" + "-" + geo_type + "_" + col_desc + "_" + col_affix + "-" + current_dt + ".csv"

    # Output the csv
    merged_df.to_csv(os.path.join(output_folder, output_file_name))


# Calling the function
accumulate_census(census_folder_path,
                  config_file,
                  'LGA',
                  col_desc='long',
                  col_affix='prefix')
