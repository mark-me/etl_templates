import json
import logging
from pathlib import Path
import pydoc

from jinja2 import Environment, FileSystemLoader
import yaml

import logging_config
from pd_document import PDDocument

logger = logging.getLogger(__name__)


def main(file_pd_ldm: str, type_template: str):
    """Creates the DDL's

    Args:
        type_template (str): The type of templates your want to use to implement your models
        models_input (str): The file that describes the models
    """
    logger.info(f"Writing implementation for {type_template}")
    # Template directory
    dir_template = "templates/" + type_template + "/"
    # Directories for output
    dir_output = "output/" + type_template + "/"
    directory = Path(dir_output)
    directory.mkdir(parents=True, exist_ok=True)

    # Loading templates
    environment = Environment(
        loader=FileSystemLoader(dir_template), trim_blocks=True, lstrip_blocks=True
    )
    dict_templates = {
        "schema": environment.get_template("create_schema.sql"),
        "table": environment.get_template("create_table.sql"),
    }

    pd_document = PDDocument(file_pd_ldm=file_pd_ldm)
    pd_document.get_MDDE_attribute()
    # TODO: Generation
        # Model - DDL Generation
            # Table
            # DDL's
            # Create schema DDL
"""         for schema in models["schemas"]:
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
"""
        # ETL
            # Updating mapping load
            # Creating stored procedures



if __name__ == "__main__":
    with open("config.yml", "r") as file:
        config = yaml.safe_load(file)
    main(file_pd_ldm=config["models_input"], type_template=config["templates"])
    pydoc.writedoc("main")
