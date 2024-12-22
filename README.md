# ETL Templating

This repository aims to use descriptions of logical data models and their lineage mappings to generate physical implementations of those model and an ETL program.

Note: so far this only implements table DDL's.

The configuration for model input and templating can be adapted in ```config.yml```. The purpose of a making the directory for templates configurable is that we can add templates for multiple database implementations that each generate different DDL outputs.

* The bare-bones example model is described as a JSON in ```input/models.json```
* An example template that generates a create table DDL is the file ```templates/dedicated-pool/create_table.sql```
* The output is a file for each DDL written in the directory ```output/dedicated-pool```

## Getting started

* Clone the repository
* Create a virtual environment and add the libraries from requirements.txt
* Run main.py

## Resources

* Templating engine: [jinja](https://jinja.palletsprojects.com/en/stable/)
* Reading XML: [xmltodict](https://pypi.org/project/xmltodict/)

## Future developments

* [Merge loading for mappings](https://techcommunity.microsoft.com/blog/azuresynapseanalyticsblog/merge-t-sql-for-dedicated-sql-pools-is-now-ga/3634331)
* [Logging](https://docs.python.org/3/howto/logging.html)
* Added example docstrings and documentation generation as inspiration. Currently the simple [pydoc](https://docs.python.org/3/library/pydoc.html) is used, as the project extends we should consider switching to [Sphinx](https://www.sphinx-doc.org/en/master/)