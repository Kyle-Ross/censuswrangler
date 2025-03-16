import os
import re


def info(
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

    # Initialise dict to contain info on the files of the metadata folder
    folder_info["metadata"]["files"] = {}

    # Loop through the metadata files and add them to that dict
    for root, dirs, files in os.walk(folder_info["metadata"]["path"]):
        for file_name_and_ext in files:
            # Split that out
            parts: tuple = os.path.splitext(file_name_and_ext)
            name: str = parts[0]
            ext: str = parts[1]
            path = os.path.join(root, name, ext)

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

    return folder_info


if __name__ == "__main__":
    from icecream import ic

    path = r"E:/Data/2021_GCP_all_for_AUS_short-header/"
    info = info(path)
    ic(info)
