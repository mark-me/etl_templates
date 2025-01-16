import datetime
import json
import logging
from pathlib import Path

import xmltodict

import logging_config
from pd_extractor_pdm import PDMObjectExtractor

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)


class PDDocumentPDM:
    """Represents Power Designer logical data model file"""

    def __init__(self, file_pd_pdm: str):
        """Extracts data from a JSON-ed version of a Power Designer document and turns it into an object representation

        Args:
            file_pd_pdm (str): JSON version of a Power Designer document (.pdm)
        """
        self.file_pd_pdm = file_pd_pdm
        self.content = self.read_file_model(file_pd_pdm=file_pd_pdm)
        # Extracting data from the file
        extractor = PDMObjectExtractor(pd_content=self.content)
        # Extracting models
        logger.debug("Start model extraction")
        self.lst_models = extractor.models()

    def read_file_model(self, file_pd_pdm: str) -> dict:
        """Reading the XML Power Designer ldm file into a dictionary

        Args:
            file_xml (str): The path to a XML file

        Returns:
            dict: The Power Designer data converted to a dictionary
        """
        # Function not yet used, but candidate for reading XML file
        with open(file_pd_pdm) as fd:
            doc = fd.read()
        dict_data = xmltodict.parse(doc)
        # TODO: Root voor PDM relevante data
        dict_data = dict_data["Model"]["o:RootObject"]["c:Children"]["o:Model"]
        return dict_data

    def __serialize_datetime(self, obj):
        """Retrieves a datetime and formats it to ISO-format

        Args:
            obj (any): Object to be formatted into the correct ISO date format if possible

        Returns:
            Datetime: Formatted in ISO-format
        """

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    def write_result(self, file_output: str):
        """Writes a json document with all the stored models and mappings to the path stored in file_document_output

        Args:
            file_output (str): The file path to which the output will be stored
        """
        dict_document = {}
        dict_document["Models"] = self.lst_models
        path = Path(file_output)
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        with open(file_output, "w") as outfile:
            json.dump(
                dict_document, outfile, indent=4, default=self.__serialize_datetime
            )
        logger.debug(f"Document output is written to '{file_output}'")


class PDDocumentPDMQuery:
    """Stores the models and mappings within a single PDDocument"""

    def __init__(self, document: PDDocumentPDM):
        """Retrieves a list of all models and a list of all mappings within a single PDDocument

        Args:
            document (PDDocument): The representation of a Power Designer logical data model
        """
        self.lst_models = document.lst_models
        # self.document = document
        # Create DDL's
        # self.write_ddl("proc", document.dict_procs)
        # self.write_ddl("view", document.dict_views)
        # self.write_ddl("view", document.lst_models["Views"])
        self.write_ddl()

    def write_ddl(self):
        """
        Creates the DDL's

        Args:
         type_template (str): The type of templates your want to use to implement your models
            dict_object (dect): The object that describes the object for the template
        """
        # Loading templates
        dest_type = "dedicated-pool"
        dir_template = "templates/" + dest_type + "/"
        environment = Environment(
            loader=FileSystemLoader(dir_template), trim_blocks=True, lstrip_blocks=True
        )
        self.dict_templates = {
            "schema": environment.get_template("create_schema.sql"),
            "Tables": environment.get_template("create_table.sql"),
            "Views": environment.get_template("create_view.sql"),
            "Procedures": environment.get_template("create_procedure.sql"),

        }
        self.__generate_ddl()

    def __generate_ddl(self):
        self.lst_template_objects = []
        for model in self.lst_models:
            for type_object, template in self.dict_templates.items():
                if type_object in model:
                    lst_objects = model[type_object]
                    for i, object in enumerate(lst_objects):
                        object["Schema"] = model["Code"]
                        lst_objects[i] = object
                    self.lst_template_objects.append(
                        {"type": type_object, "template": template, "objects": lst_objects})
                else:
                    logger.warning(f"Object for '{type_object}' does not exist in the model.")

            self.__write_ddl()
        return self.lst_template_objects

    def __write_ddl(self):

        for type in self.lst_template_objects:
            for object in type["objects"]:
                print(type["type"])
                dir_output = "output/" + type["type"] + "/"
                directory = Path(dir_output)
                directory.mkdir(parents=True, exist_ok=True)
                content = self.dict_templates[type["type"]].render(item=object)
                file_output = dir_output + "Schema" + "_" + object["Code"] + ".sql"
                with open(file_output, mode="w", encoding="utf-8") as file_ddl:
                    file_ddl.write(content)
                logger.info(f"Written Table DDL {file_output}")

if __name__ == "__main__":
    file_model = "input/MDDE (PDM).pdm"  # "input/ExampleDWH.ldm"
    file_document_output = "output/MDDE_PDM.json"  # "output/ExampleDWH.json"
    document = PDDocumentPDM(file_pd_pdm=file_model)
    documentQ = PDDocumentPDMQuery(document=document)
    # Saving model objects
    document.write_result(file_output=file_document_output)
    # lst_models = document.get_MDDE_model()
    # lst_entities = document.get_MDDE_entity()
    # lst_attributes = document.get_MDDE_attribute()
    print("Done")
