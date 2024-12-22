import json
from pathlib import Path
import pprint
import pydoc
import yaml

from jinja2 import Environment, FileSystemLoader
import xmltodict

def main(type_template: str, models_input: str):
    """Creates the DDL's

    Args:
        type_template (str): The type of templates your want to use to implement your models
        models_input (str): The file that describes the models
    """
    # Main
    dir_template = "templates/" + type_template + "/"
    dir_output = "output/" + type_template + "/"

    # Load model data
    with open(models_input) as json_file:
        models = json.load(json_file)

    # For loading templates
    environment = Environment(
        loader=FileSystemLoader(dir_template), trim_blocks=True, lstrip_blocks=True
    )

    # Create output directory
    Path(dir_output).mkdir(parents=True, exist_ok=True)

    # Generation
    # Create schema
    tpl_create_schema = environment.get_template("create_schema.sql")
    for schema in models["schemas"]:
        # Create schema DDL
        content = tpl_create_schema.render(schema=schema)
        file_output = dir_output + schema["name"] + ".sql"
        with open(file_output, mode="w", encoding="utf-8") as file_ddl:
            file_ddl.write(content)

        # Creating table DDL's
        tpl_create_table = environment.get_template("create_table.sql")
        for table in schema["tables"]:
            content = tpl_create_table.render(
                schema=schema, table=table, columns=table["columns"]
            )
            file_output = dir_output + schema["name"] + "_" + table["name"] + ".sql"
            with open(file_output, mode="w", encoding="utf-8") as file_ddl:
                file_ddl.write(content)

        # Creating view DDL's
        # Updating mapping load
        # Creating stored procedures


def xml_to_dict(file_xml: str) -> dict:
    """Converting XML files describing models to Python dictionaries

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
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    main(type_template=config["templates"], models_input=config["models_input"])
    pydoc.writedoc("main")
