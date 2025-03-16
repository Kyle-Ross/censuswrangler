import os


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

    return folder_info


if __name__ == "__main__":
    from icecream import ic

    path = r"E:/Data/2021_GCP_all_for_AUS_short-header/"
    info = info(path)
    ic(info)
