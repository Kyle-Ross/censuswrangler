"""Defining pandera schemas which will be used for dataframe validation."""

import pandera as pa

config_schema = pa.DataFrameSchema(
    {
        "SHORT": pa.Column(str),
        "LONG": pa.Column(str),
        "DATAPACKFILE": pa.Column(str),
        "CUSTOM_DESCRIPTION": pa.Column(str),
        "CUSTOM_GROUP": pa.Column(str),
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
