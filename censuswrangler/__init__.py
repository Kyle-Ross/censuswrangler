"""
censuswrangler package.

This package provides tools for extracting census data from the Australian Bureau of Statistics (ABS) datapack structure. 
It includes utilities for managing datapack outputs using validated configuration templates.

Interface:
- create_config_template: Function to create a configuration template csv.
- Census: Class for managing, extracting and outputing census data from the datapack structure.
"""

from censuswrangler.config import create_config_template
from censuswrangler.census import Census

__all__ = ["create_config_template", "Census"]
