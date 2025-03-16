import os
import re

from censuswrangler import _pack

from icecream import ic

path = r"E:/Data/2021_GCP_all_for_AUS_short-header/"
info = _pack.info(path)

# Initialise storage for file details
info["metadata"]["files"] = {}

regex_metadata = r'^Metadata_'
regex_sequential = r""

for root, dirs, files in os.walk(info["metadata"]["path"]):
    for file_name_and_ext in files:
        # Split that out
        parts: tuple = os.path.splitext(file_name_and_ext)
        name: str = parts[0]
        ext: str = parts[1]
        path = os.path.join(root, name, ext)

        def assert_type(ext: str, expected_ext:str, file_desc: str):
            """Check that that an extension is what was expected"""
            assert ext.lower() == expected_ext, f"Expected '{file_desc}' to be file type '{expected_ext}, instead got type '{ext}'"

        # Identify the files, check their types
        file_desc = ""
        if bool(re.match(r'^Metadata_', name)):
            desc = "metadata"
            assert_type(ext, ".xlsx", desc)
            file_desc = desc
        elif bool(re.search(r'_Sequential_Template_', name)):
            desc = "sequential_template"
            assert_type(ext, ".xlsx", desc)
            file_desc = desc
        elif bool(re.search(r'_geog_desc_', name)):
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

        info["metadata"]["files"][file_desc] = file_info
        


        # file_list.append(os.path.join(root, name, ext))

ic(info)
