About
=================================

CensusWrangler is the fast python API to your local copy of the Australian Census data.

The use-case
----------------------------------

If you have any interest or career involving Australian data, you've likely had to deal with the challenging Census data structures.

In the government's interest of maintaining privacy for all involved, they provide data as a series of hundreds of tables each at different levels of geographic aggregation.

My experience has been that getting the right slice of data out this structure can be tedious and time-consuming. It drags out what would otherwise be a quick piece of adhoc analysis.

If you're lucky - your organisation already has a paid API, or database of the census data. But if not?

You can speed up the process with the CensusWrangler library. With quick & templatable configurations it helps you efficiently pull data out of the downloadable census datapacks.

Features
----------------------------------

- **Configuration templates**: Deploy and quickly customise configuration csvs - then let CensusWrangler instally find and merge the data
- **Re-use configs across geographies**: Change a single argument to re-pull data from a different geography without any additional work
- **Validation & Checks**: Your config is checked against census metadata, with detailed errors letting you know what went wrong
- **Built-in Grouping**: Make easier for yourself down the line by setting groups and your own column naming directly in the config file
- **Customisable output**: Select from several convenient output methods, accessing the output quickly in your desired format
- **On you local machine**: Once you have downloaded the datapack, the library requires no access to anything other than what is on your local machine

Set-up 
----------------------------------

Download a census datapack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Visit the the `ABS Census DataPacks <https://www.abs.gov.au/census/find-census-data/datapacks>`_ page & download a datapack ``.zip``
2. Extract the ``.zip`` into a single folder, containing nothing else

When you are ready, your datapack folder should look something like this, with the name of the downloaded pack:

.. literalinclude :: _static/datapack_directory_example.txt
   :language: text


.. note:: CensusWrangler is fully tested on the 2021 census datapacks, and basic testing shows it working with previous years as well

Install
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::
   
   pip install censuswrangler


Import 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python
   
   import censuswrangler as cw

Usage
----------------------------------

Preparing a Config Template
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
We tell CensusWrangler what data to grab by preparing a config ``csv``:

Generate a config template
""""""""""""""""""""""""""""""""""
You can quickly generate a template to get started:

.. code-block:: python
   
   cw.create_config_template("C:\Config Folder\")

Config fields
""""""""""""""""""""""""""""""""""

Below is an sample example of the config ``csv```

The first 3 fields come straight from the metadata:

- ``SHORT`` - Short descriptor
- ``LONG`` - Long descriptor
- ``DATAPACKFILE`` - A code indicating which datapack file contains the field

The other 2 are used to customise, group & simplify the names of fields in the CensusWrangler output:

- ``CUSTOM_DESCRIPTION`` - Describes the data subset represented, Like 'Male' & 'Female'
- ``CUSTOM_GROUP`` - Describes the subsets, like 'Gender'

Put whatever you need in the custom fields, just make sure that each row is unique.

.. list-table::
   :widths: 20 40 10 15 15
   :header-rows: 1

   * - SHORT
     - LONG
     - DATAPACKFILE
     - CUSTOM_DESCRIPTION
     - CUSTOM_GROUP
   * - Tot_P_M
     - Total_Persons_Males
     - G01
     - Male
     - Gender
   * - Tot_P_F
     - Total_Persons_Females
     - G01
     - Female
     - Gender
   * - P_Tot_Marrd_reg_marrge
     - PERSONS_Total_Married_in_a_registered_marriage
     - G06
     - Married
     - Relationship Type
   * - P_Tot_Married_de_facto
     - PERSONS_Total_Married_in_a_de_facto_marriage
     - G06
     - Couple
     - Relationship Type
   * - P_Tot_Not_married
     - PERSONS_Total_Not_married
     - G06
     - No relationship
     - Relationship Type

Referencing Metadata
""""""""""""""""""""""""""""""""""

It's super easy to copy what you want out of the metadata file that comes with each datapack. 

1. In the datapack folder, look in the ``/Metadata/`` folder for a file like ``Metadata_2021_GCP_DataPack_R1_R2.xlsx``
2. Go to the ``Cell Descriptors Information`` sheet
3. Browse the fields, and copy over the ``SHORT``, ``LONG`` & ``DATAPACKFILE`` columns for your fields you want, into the config file
4. Fill in the custom fields in the remaining columns of the config file

This file is also used to validate your config selections, so try & avoiding changing it as you go.

Select a Census Geography
""""""""""""""""""""""""""""""""""
Visit the ABS `Census Geography Glossary <https://www.abs.gov.au/census/guide-census-data/geography/census-geography-glossary>`_.

Determine the shortcode for the geography you are after. For example, 'Statistical Area Level 1' has code 'SA1'.

This is also reflected by the folder names in the datapack - look for the name like ``\2021 Census GCP All Geographies for AUS\``.

Usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once the config file is ready, you can run CensusWrangler with just a few lines of code:

.. literalinclude :: _static/workflow_example.py
   :language: python3

More details are available in the `documentation <www.google.com>`_.

Example Output
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can see example output over in the repository's `sample folder <https://github.com/Kyle-Ross/censuswrangler/tree/main/samples>`_.

_______________________________________________________


Good luck - and don't forget to give the `repository <https://github.com/Kyle-Ross/censuswrangler>`_ a star if this helped you out (it all helps!).
