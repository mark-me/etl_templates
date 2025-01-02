import datetime
import json
import logging
from pathlib import Path

import xmltodict

import logging_config
from pd_object_extractor import ObjectExtractor

logger = logging.getLogger(__name__)


class PDDocument:
    """Represents Power Designer logical data model file"""

    def __init__(self, file_pd_ldm: str):
        """Extracts data from a JSON-ed version of a Power Designer document and turns it into an object representation

        Args:
            file_pd_ldm (str): JSON version of a Power Designer document (.ldm)
        """
        self.file_pd_ldm = file_pd_ldm
        self.content = self.read_file_model(file_pd_ldm=file_pd_ldm)
        # Extracting data from the file
        extractor = ObjectExtractor(pd_content=self.content)
        # Extracting models
        logger.debug("Start model extraction")
        self.lst_models = extractor.models()
        # Extract mappings
        logger.debug("Start mapping extraction")
        dict_entities = self.__all_entities()
        dict_attributes = self.__all_attributes()
        # self.lst_mappings = extractor.mappings(
        #     dict_entities=dict_entities, dict_attributes=dict_attributes
        # )

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
                    "ModelID": model["Id"],
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
                            "id_model": model["Id"],
                            "NameModel": model["Name"],
                            "CodeModel": model["Code"],
                            "IsDocumentModel": not model["IsDocumentModel"],
                            "IdEntity": entity["Id"],
                            "NameEntity": entity["Name"],
                            "CodeEntity": entity["Code"],
                        }
        return dict_result

    def __serialize_datetime(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

    def write_result(self, file_output: str):
        dict_document = {}
        dict_document['Models'] = self.lst_models
        path = Path(file_output)
        Path(path.parent).mkdir(parents=True, exist_ok=True)
        with open(file_output, "w") as outfile:
            json.dump(dict_document, outfile, indent=4, default=self.__serialize_datetime)
        logger.debug(f"Document output is written to '{file_output}'")

class PDDocumentQuery:
    def __init__(self):
        pass

    def get_MDDE_model(self) -> list:
        lst_result = []
        for model in self.lst_models:
            dict_selection = {
                "ModelID": model["TargetID"],
                "Name": model["Name"],
                "Code": model["Name"],
                "CreationDate": model["CreationDate"],
                "ModificationDate": model["ModificationDate"],
            }
            lst_result.append(dict_selection)
        return lst_result

    def get_MDDE_entity(self) -> list:
        lst_results = []
        for model in self.lst_models:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                dict_selection = {
                    "EntityID": entity["ObjectID"],
                    "ModelID": model["TargetID"],
                    "EntityName": entity["Name"],
                    "EntityCode": entity["Code"],
                    "EntitySchema": model[
                        "Code"
                    ],  # TODO: Reroute schema, now comes from entity, can be set at model level?
                    "EntityIsShortcut": str(not model["IsDocumentModel"]),
                    "EntityOrgID": "",  # TODO: When and how used?
                    "ModelOrgID": "",  # TODO: When and how used?
                    "CreationDate": entity["CreationDate"],
                    "ModificationDate": entity["ModificationDate"],
                }
                lst_results.append(dict_selection)
        return lst_results

    def get_MDDE_attribute(self) -> list:
        # TODO: Complete
        lst_results = []
        # Only the attributes of the non-source model should be deployed
        models_document = [
            model for model in self.lst_models if model["IsDocumentModel"]
        ]
        for model in models_document:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                lst_attributes = entity["Attributes"]
                for attr in lst_attributes:
                    dict_selection = {"AttributeID": attr["ObjectID"]}
                    lst_results.append(dict_selection)

        return lst_results


if __name__ == "__main__":
    file_model = "input/ExampleDWH.ldm"
    file_document_output = "output/ExampleDWH.json"
    document = PDDocument(file_pd_ldm=file_model)
    # Saving model objects
    document.write_result(file_output=file_document_output)
    # lst_models = document.get_MDDE_model()
    # lst_entities = document.get_MDDE_entity()
    # lst_attributes = document.get_MDDE_attribute()
    print("Done")
