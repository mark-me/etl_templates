# ETL Templating

This repository aims to deploy descriptions of logical data models and descriptions of model lineage mappings to fill those models with data for multiple technical solutions.

Be warned: this code is still far from the stated goal and currently just implements data model implementations using 'create schema' and 'create table' DDLs for [dedicated DQL pool](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-overview-what-is) and [duckdb](https://duckdb.org/).

The configuration for model input and templating can be adapted in ```config.yml```. The purpose of a making the directory for templates configurable is that we can add templates for multiple database implementations that each generate different DDL outputs.

* The bare-bones example theorethical model is described as a JSON in ```input/models.json```, but need to be replaced by  [PowerDesigner XML's. See the section [Sample XML conversion](#sample-xml-conversion)
* An example template that generates a create schema DDL is the file ```templates/{implementation}/create_schema.sql```
* An example template that generates a create table DDL is the file ```templates/{implementation}/create_table.sql```
* The output is a file for each DDL written in the directory ```output/{implementation}```

Logs are written as JSON in the terminal and to log.json.

## Getting started

* Clone the repository
* Create a virtual environment and add the libraries from ```requirements.txt```
* Run ```main.py```
* To run an example for a duckdb deployment you can run ```duckdb_deploy.py``` after you ran the duckdb example in main. The resulting database can be found in ```output/duckdb/duckdb.db```, which can be browsed with [dbeaver](https://duckdb.org/docs/guides/sql_editors/dbeaver.html).

### Sample XML conversion

The current code is based on my own sample data structure, but we want to move to PowerDesigner generated model data. As a starting point the [example model](https://generate.x-breeze.com/docs/3.1/Examples/) XML's from [CrossBreeze](https://crossbreeze.nl/) are added to the repository (```input/model_source.xml``` and ```input/model_dwh.xml```). The script ```xml_to_json.py``` can be used to convert them to more human readable JSON to analyze the data to be used for this project.

## Resources

* Documentation on how to create templates using the [Jinja templating engine](https://jinja.palletsprojects.com/en/stable/)
* Reading XML and turning them into [dictionaries](https://realpython.com/python-dicts/): [xmltodict](https://pypi.org/project/xmltodict/)

## Future developments

* [Merge loading for mappings](https://techcommunity.microsoft.com/blog/azuresynapseanalyticsblog/merge-t-sql-for-dedicated-sql-pools-is-now-ga/3634331)
* Added example docstrings and documentation generation as inspiration. Currently the simple [pydoc](https://docs.python.org/3/library/pydoc.html) is used, as the project extends we should consider switching to [Sphinx](https://www.sphinx-doc.org/en/master/)
* Antecedents and precedents reporting for escalation business processes using [graphs](https://python.igraph.org/en/latest/tutorial.html) and [graph visualizations](https://networkx.org/)
