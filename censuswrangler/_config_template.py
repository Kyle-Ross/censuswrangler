import pandas as pd
import pandera as pa

# Pandera schema on which the config template will be validated
template_schema = pa.DataFrameSchema(
    {
        "DATA_FILE_CODE": pa.Column(str),
        "FIELD_SHORT": pa.Column(str),
        "FIELD_LONG": pa.Column(str),
        "VALUE_DESC": pa.Column(str),
        "GROUP": pa.Column(str),
    }
)