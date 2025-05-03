import censuswrangler as cw

# Intialise the Census object
census = cw.Census(
    datapack_path=r"E:/Data/2021_GCP_all_for_AUS_short-header/",  # Datapack folder path
    config_path=r"censuswrangler/config_template.csv",  # Config file path
    geo_type="LGA",  # 3 letter geotype code
    year=2021,  # The census year
)

# Gather and prepare the data from the datapack
census.wrangle("all")  # "merge" | "pivot" | "all"

# Access the output dataframes in the desired format
print(census.merged_df)
print(census.pivoted_df)

# Or output directly to csv
census.to_csv(
    "all",  # "merge" | "pivot" | "all"
    r"F:/Github/censuswrangler/test_output",  # Output folder
)
