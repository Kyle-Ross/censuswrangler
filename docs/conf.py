from datetime import datetime
import toml
import sys
import os

# Add the target directory(s) to the Python path.
sys.path.insert(0, os.path.abspath("../censuswrangler"))

# Accessing the poetry config toml file
pyproject_toml = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../pyproject.toml"
)
with open(pyproject_toml, "r") as f:
    poetry_toml = toml.load(f)

# Use the name from pyproject.toml
project = poetry_toml["tool"]["poetry"]["name"]

# Set copyright with the current year
current_year = datetime.now().year
copyright = f"{current_year}, Kyle Ross"

# Use the author from pyproject.toml
author = poetry_toml["tool"]["poetry"]["authors"][0]

# Use the release from pyproject.toml
release = poetry_toml["tool"]["poetry"]["version"]

# Set extensions
extensions = [
    # Automatically document your Python code via docstrings
    "sphinx.ext.autodoc",
    # Support for Google and NumPy style docstrings
    # By default will ignore private objects with _leading underscore
    "sphinx.ext.napoleon",
    # Adds emoji compatibility
    "sphinxemoji.sphinxemoji",
]

# Default options for every rst file
autodoc_default_options = {
    "members": True,
    "show-inheritance": False,
    "undoc-members": False,
}

# Other autodoc config
autoclass_content = "class"
autodoc_class_signature = "separated"
autodoc_member_order = "groupwise"

# Set your HTML stuff here
templates_path = ["_templates"]
html_theme = "sphinxawesome_theme"  # nltk_theme, furo, sphinxawesome_theme
html_static_path = ["_static"]
# html_logo = "_static/logo.png"
html_show_sourcelink = False

# Code blocks
highlight_language = "python3"
pygments_style = "borland"
pygments_style_dark = "nord"

# Object signatures

# Value of 1 means every argument is on its own line
maximum_signature_line_length = 1

# Ride the repeating parent paths from the toctree
toc_object_entries_show_parents = "hide"

# Removes appended module names in autodocs
add_module_names = True

# Ref
# https://www.sphinx-doc.org/en/master/usage/configuration.html
