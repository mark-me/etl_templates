import json
import logging
from pathlib import Path

import xmltodict

import logging_config
from pd_object_extractor import ObjectExtractor
from pd_object_transformer import ObjectTransformer

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
        self.lst_models = extractor.model_data()

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

    def get_MDDE_model(self):
        lst_result = []
        for model in self.lst_models:
            dict_selection = {
                "ModelID": model["TargetID"],
                "Name": model["Name"],
                "Code": model["Name"],
                "CreationDate": model["CreationDate"],
                "ModificationDate": model["ModificationDate"]
            }
            lst_result.append(dict_selection)
        return lst_result

    def get_MDDE_entity(self) -> list:
        lst_results = []
        for model in self.lst_models:
            id_target = model["TargetID"]
            name_schema = model["Code"]
            lst_entities = model["Entities"]
            is_shortcut = not model["IsDocumentModel"]
            for entity in lst_entities:
                dict_selection = {
                    "EntityID": entity["ObjectID"],
                    "ModelID": id_target,
                    "EntityName": entity["Name"],
                    "EntityCode": entity["Code"],
                    "EntitySchema": name_schema,  # TODO: Reroute schema, now comes from entity, can be set at model level?
                    "EntityIsShortcut": str(is_shortcut),
                    "EntityOrgID": "",      # TODO: When and how used?
                    "ModelOrgID": "",       # TODO: When and how used?
                    "CreationDate": entity["CreationDate"],
                    "ModificationDate": entity["ModificationDate"]
                }
                lst_results.append(dict_selection)
        return lst_results

    def get_MDDE_attribute(self) -> list:
        # TODO: Complete
        lst_results = []
        # Only the attributes of the non-source model should be deployed
        models_document = [model for model in self.lst_models if model["IsDocumentModel"]]
        for model in models_document:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                id_entity = entity["ObjectID"]
                lst_attributes = entity["Attributes"]
                for attr in lst_attributes:
                    dict_selection = {
                        "AttributeID": attr["ObjectID"]
                    }
                    lst_results.append(dict_selection)

        return lst_results


if __name__ == "__main__":
    file_model = "input/ExampleDWH.ldm"
    document = PDDocument(file_pd_ldm=file_model)
    # Saving model objects
    lst_models = document.get_MDDE_model()
    lst_entities = document.get_MDDE_entity()
    lst_attributes = document.get_MDDE_attribute()
    print("Done")
