import datetime
import json
from pathlib import Path
import os
import sys

import xmltodict

if __name__ == "__main__":
    sys.path.append(os.getcwd())

from src.log_config.logging_config import logging
from pd_extractor import ObjectExtractor

logger = logging.getLogger(__name__)


class PDDocument:
    """Represents Power Designer logical data model file"""

    def __init__(self, file_pd_ldm: str):
        """Extracts data from Logical Model Power Designer document and turns it into an object representation

        Args:
            file_pd_ldm (str): Power Designer logical data model document (.ldm)
        """
        logger.info("Ik ben er")
        self.file_pd_ldm = file_pd_ldm
        # Extracting data from the file
        self.content = self.read_file_model(file_pd_ldm=file_pd_ldm)
        self.lst_models = []
        self.lst_mappings = []

    def get_models(self):
        """Retrieves model data separately from the mappings

        Returns:
            list: The Power Designer models without any mappings
        """
        extractor = ObjectExtractor(pd_content=self.content)
        logger.debug("Start model extraction")
        lst_models = extractor.models()
        logger.debug("Finished model extraction")
        self.lst_models = lst_models
        return lst_models

    def get_mappings(self):
        """Retrieves mapping data

        Returns:
            list: The Power Designer mappings within the models
        """
        # If self.lst_models is not filled, fill
        if len(self.lst_models) == 0:
            self.get_models()

        extractor = ObjectExtractor(pd_content=self.content)
        logger.debug("Start mapping extraction")
        dict_entities = self.__all_entities()
        dict_attributes = self.__all_attributes()
        logger.debug("get lst_mappings")
        # This is where it goes wrong :)
        lst_mappings = extractor.mappings(
            dict_entities=dict_entities, dict_attributes=dict_attributes
        )
        logger.debug("Finished mapping extraction")
        self.lst_mappings = lst_mappings
        return lst_mappings

    def read_file_model(self, file_pd_ldm: str) -> dict:
        """Reading the XML Power Designer ldm file into a dictionary

        Args:
            file_xml (str): The path to a XML file

        Returns:
            dict: The Power Designer data converted to a dictionary
        """
        # Function not yet used, but candidate for reading XML file
        with open(file_pd_ldm) as fd:
            doc = fd.read()
        dict_data = xmltodict.parse(doc)
        dict_data = dict_data["Model"]["o:RootObject"]["c:Children"]["o:Model"]
        return dict_data

    def __all_entities(self) -> dict:
        """Retrieves all entities regardless of the model they belong to

        Returns:
            dict: Each dictionary value represents an entity, the key is the internal ID
        """
        dict_result = {}
        for model in self.lst_models:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                dict_result[entity["Id"]] = {
                    "Id": entity["Id"],
                    "Name": entity["Name"],
                    "Code": entity["Code"],
                    "IdModel": model["Id"],
                    "NameModel": model["Name"],
                    "CodeModel": model["Code"],
                    "IsDocumentModel": not model["IsDocumentModel"],
                }
        return dict_result

    def __all_attributes(self) -> dict:
        """Retrieves all attributes regardless of the model or entity they belong to

        Returns:
            dict: Each dictionary value represents an attribute, the key is the internal ID
        """
        dict_result = {}
        for model in self.lst_models:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                if "Attributes" in entity:
                    lst_attributes = entity["Attributes"]
                    for attr in lst_attributes:
                        dict_result[attr["Id"]] = {
                            "Id": attr["Id"],
                            "Name": attr["Name"],
                            "Code": attr["Code"],
                            "IdModel": model["Id"],
                            "NameModel": model["Name"],
                            "CodeModel": model["Code"],
                            "IsDocumentModel": not model["IsDocumentModel"],
                            "IdEntity": entity["Id"],
                            "NameEntity": entity["Name"],
                            "CodeEntity": entity["Code"],
                        }
        return dict_result

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
        lst_models = self.get_models()
        lst_mappings = self.get_mappings()
        dict_document["Models"] = lst_models
        dict_document["Mappings"] = lst_mappings
        path = Path(file_output)
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        with open(file_output, "w") as outfile:
            json.dump(
                dict_document, outfile, indent=4, default=self.__serialize_datetime
            )
        logger.debug(f"Document output is written to '{file_output}'")


if __name__ == "__main__":
    file_model = "input/Example_CL_LDM.ldm"  # "input/ExampleDWH.ldm"
    file_document_output = "output/Example_CL_LDM_new.json"  # "output/ExampleDWH.json"
    document = PDDocument(file_pd_ldm=file_model)
    # Saving model objects
    document.write_result(file_output=file_document_output)
    # lst_models = document.get_MDDE_model()
    # lst_entities = document.get_MDDE_entity()
    # lst_attributes = document.get_MDDE_attribute()
    print("Done")
