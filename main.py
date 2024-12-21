import json
from pathlib import Path
import pprint
import pydoc
import yaml

from jinja2 import Template
import xmltodict

# Input parameters
with open('config.yml', 'r') as file:
    config = yaml.safe_load(file)
type_template = config["templates"] #: Subdirectory containing dedicated pool templates
models_input = config["models_input"]

def main(type_template: str, models_input: str):
    """Creates the DDL's

    Args:
        type_template (str): The type of templates your want to use to implement your models
        models_input (str): The file that describes the models
    """
    # Main
    dir_template = "templates/" + type_template + "/"
    dir_output = "output/" + type_template + "/"

    with open(models_input) as json_file:
        models = json.load(json_file)

    # Create output directory
    Path(dir_output).mkdir(parents=True, exist_ok=True)

    # Generation
    for schema in models["schemas"]:

        # Creating table DDL's
        with open(dir_template + "create_table.sql", 'r') as file:
            ddl_create_table = file.read()
        for table in schema["tables"]:
            ddl_statement = Template(ddl_create_table, trim_blocks=True, lstrip_blocks=True).render(
                schema=schema, table=table, columns=table["columns"]
            )
            file_output = dir_output + schema["name"] + "_" + table["name"] + ".sql"
            with open(file_output, "w") as file_ddl:
                file_ddl.write(ddl_statement)

        # Creating view DDL's
        # Updating mapping load
        # Creating stored procedures

def xml_to_dict(file_xml: str) -> dict:
    """ Converting XML files describing models to Python dictionaries

    Args:
        file_xml (str): The path to a XML file

    Returns:
        dict: The data converted to a dictionary
    """
    # Function not yet used, but candidate for reading XML file
    with open(file_xml) as fd:
        doc = xmltodict.parse(fd.read())
    dict_doc = json.dumps(xmltodict.parse(doc))
    pprint.pprint(dict_doc)
    return dict_doc

if __name__ == "__main__":
    main(type_template=type_template, models_input=models_input)
    pydoc.writedoc('main')