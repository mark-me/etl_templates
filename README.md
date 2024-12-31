# ETL Templating

This repository aims to deploy descriptions of logical data models and descriptions of model lineage mappings to fill those models with data for multiple technical solutions.

Be warned: this code is still far from the stated goal and currently just implements data model implementations using 'create schema' and 'create table' DDLs for [dedicated SQL pool](https://learn.microsoft.com/en-us/azure/synapse-analytics/sql-data-warehouse/sql-data-warehouse-overview-what-is) and [duckdb](https://duckdb.org/).

The configuration for model input and templating can be adapted in ```config.yml```. The purpose of a making the directory for templates configurable is that we can add templates for multiple database implementations that each generate different DDL outputs.

* The bare-bones example theorethical model is described as a JSON in ```input/models.json```, but need to be replaced by PowerDesigner XML's. See the section [Sample XML conversion](#sample-xml-conversion)
* The [Jinja templating engine](https://jinja.palletsprojects.com/en/stable/templates/) is used to generate implementations. Two example templates are added:
  * a create schema DDL template ```templates/{implementation}/create_schema.sql```
  * a create table DDL template ```templates/{implementation}/create_table.sql```
* The output is a file for each DDL written in the directory ```output/{implementation}```

Logs are written as JSON in the terminal and to log.json. The logging configuration is implemented in the file ```logging_config.py```.

## Getting started

* Clone the repository
* Create a virtual environment and add the libraries from ```requirements.txt```
* Run ```main.py```
* To run an example for a duckdb deployment you can run ```duckdb_deploy.py``` after you ran the duckdb example in main. The resulting database can be found in ```output/duckdb/duckdb.db```, which can be browsed with [dbeaver](https://duckdb.org/docs/guides/sql_editors/dbeaver.html).

### Sample XML conversion

The current code is based on my own sample data structure, but we want to move to PowerDesigner generated model data. As a starting point the [example model](https://generate.x-breeze.com/docs/3.1/Examples/) documents from [CrossBreeze](https://crossbreeze.nl/) are added to the repository (```input/model_source.xml``` and ```input/ExampleDWH.ldb```). The script ```model.py``` is the entry point for extracting data into objects. Objectdata can be written to JSON files by using the ```model.save_objects_json``` method, which will be dumped in de output directory.

[xmltodict](https://pypi.org/project/xmltodict/) is used to convert XML into Python [dictionaries](https://realpython.com/python-dicts/), which in turn can be written to a JSON file.


## Power Designer

[Presentation](https://docs.google.com/presentation/d/e/2PACX-1vSz0YO-Zb-OxNcQNjBMmwl-HqMe3lqDiZ2mH8qlQZGwpCddTSVQRgFPpJm3Dkvh5JsThuhzpjZtZWUj/pub?start=false&loop=false&delayms=3000) on  Power Designer's nomenclature

## Future developments

* Create templates and procedures for testing on model constraints:
  * Entity identifier
  * Relationships
* Add more elaborate logging
* Added example docstrings and documentation generation as inspiration. Currently the simple [pydoc](https://docs.python.org/3/library/pydoc.html) is used, as the project extends we should consider switching to [Sphinx](https://www.sphinx-doc.org/en/master/)
* Antecedents and precedents reporting for escalation business processes using [graphs](https://python.igraph.org/en/latest/tutorial.html) and [graph visualizations](https://networkx.org/). [Tutorial](https://www.youtube.com/watch?v=D8zXTiOLrYA&ab_channel=PythonTutorialsforDigitalHumanities)
* [Merge loading for mappings](https://techcommunity.microsoft.com/blog/azuresynapseanalyticsblog/merge-t-sql-for-dedicated-sql-pools-is-now-ga/3634331)
