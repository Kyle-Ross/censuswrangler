"""Defining pandera schemas which will be used for validation of things like the config file."""

import pandera as pa

config_schema = pa.DataFrameSchema(
    {
        "DATA_FILE_CODE": pa.Column(str),
        "FIELD_SHORT": pa.Column(str),
        "FIELD_LONG": pa.Column(str),
        "VALUE_DESC": pa.Column(str),
        "GROUP": pa.Column(str),
    }
)

metadata_schema = pa.DataFrameSchema(
    {
        "sequential": pa.Column(str),
        "short": pa.Column(str),
        "long": pa.Column(str),
        "datapackfile": pa.Column(str),
        "profiletable": pa.Column(str),
        "columnheadingdescriptioninprofile": pa.Column(str),
    }
)
