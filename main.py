import json
import logging
import pydoc
import yaml

from jinja2 import Environment, FileSystemLoader

import logging_config

logger = logging.getLogger(__name__)


def main(type_template: str, models_input: str):
    """Creates the DDL's

    Args:
        type_template (str): The type of templates your want to use to implement your models
        models_input (str): The file that describes the models
    """
    logger.info(f"Writing implementation for {type_template}")
    dir_template = "templates/" + type_template + "/"
    dir_output = "output/" + type_template + "/"

    # Loading templates
    environment = Environment(
        loader=FileSystemLoader(dir_template), trim_blocks=True, lstrip_blocks=True
    )
    dict_templates = {
        "schema": environment.get_template("create_schema.sql"),
        "table": environment.get_template("create_table.sql"),
    }

    # Load model data
    with open(models_input) as json_file:
        models = json.load(json_file)
    logger.info(f"Read models from {models_input}")

    # Generation
    for schema in models["schemas"]:
        # Create schema DDL
        content = dict_templates["schema"].render(schema=schema)
        file_output = dir_output + schema["name"] + ".sql"
        with open(file_output, mode="w", encoding="utf-8") as file_ddl:
            file_ddl.write(content)
        logger.info(f"Written Schema DDL {file_output}")

        # Creating table DDL's
        for table in schema["tables"]:
            content = dict_templates["table"].render(
                schema=schema, table=table, columns=table["columns"]
            )
            file_output = dir_output + schema["name"] + "_" + table["name"] + ".sql"
            with open(file_output, mode="w", encoding="utf-8") as file_ddl:
                file_ddl.write(content)
            logger.info(f"Written Table DDL {file_output}")

        # Creating view DDL's
        # Updating mapping load
        # Creating stored procedures


if __name__ == "__main__":
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    main(type_template=config["templates"], models_input=config["models_input"])
    pydoc.writedoc("main")
