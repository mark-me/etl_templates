import json
import logging
from pathlib import Path

import xmltodict

import logging_config
from pd_object_extractor import ObjectExtractor
from pd_object_cleaner import ObjectCleaner

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

        extractor = ObjectExtractor(pd_content=self.content)

        self.lst_models = extractor.extract_model_data()
        self.lst_domains = extractor.extract_domain_data()

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
        # dict_data = remove_a_key(dict_data, "a:CreationDate")
        # dict_data = remove_a_key(dict_data, "a:ModificationDate")
        # dict_data = remove_a_key(dict_data, "a:Creator")
        # dict_data = remove_a_key(dict_data, "a:Modifier")
        # dict_data = remove_a_key(dict_data, "a:History")
        return dict_data

    def remove_a_key(self, d: dict, remove_key: str) -> dict:
        """Remove keys from a nested dictionary, also from the dictionaries within lists (Currently not used)

        Args:
            d (dict): Dictionary that needs cleaning
            remove_key (str): The name of the keys that needs to be removed

        Returns:
            dict: The dictionary without the keys
        """
        if isinstance(d, dict):
            for key in list(d.keys()):
                if key == remove_key:
                    del d[key]
                else:
                    self.remove_a_key(d[key], remove_key)
            return d
        elif isinstance(d, list):
            for i in range(len(d)):
                d[i] = self.remove_a_key(d[i], remove_key)
            return d


    def get_MDDE_model(self):
        lst_result = []
        for model in self.lst_models:
            dict_selection = {
                "ModelID": model["a:TargetID"],
                "Name": model["a:Name"],
                "Code": model["a:Name"],
                "CreationDate": model["a:CreationDate"],
                "ModificationDate": model["a:ModificationDate"]
            }
            lst_result.append(dict_selection)
        return lst_result

    def get_MDDE_entity(self) -> list:
        lst_results = []
        for model in self.lst_models:
            id_target = model["a:TargetID"]
            name_schema = model["a:Code"]
            lst_entities = model["entities"]
            is_shortcut = not model["is_document_model"]
            for entity in lst_entities:
                dict_selection = {
                    "EntityID": entity["a:ObjectID"],
                    "ModelID": id_target,
                    "EntityName": entity["a:Name"],
                    "EntityCode": entity["a:Code"],
                    "EntitySchema": name_schema,  # TODO: Reroute schema, now comes from entity, can be set at model level?
                    "EntityIsShortcut": str(is_shortcut),
                    "EntityOrgID": "",      # TODO: When and how used?
                    "ModelOrgID": "",       # TODO: When and how used?
                    "CreationDate": entity["a:CreationDate"],
                    "ModificationDate": entity["a:ModificationDate"]
                }
                lst_results.append(dict_selection)
        return lst_results

    def get_MDDE_attribute(self) -> list:
        lst_results = []
        # Only the attributes of the non-source model should be deployed
        models_document = [model for model in self.lst_models if model["is_document_model"]]
        for model in models_document:
            lst_entities = model["entities"]
            for entity in lst_entities:
                id_entity = entity["a:ObjectID"]
                lst_attributes = entity["attributes"]
                for attr in lst_attributes:
                    dict_selection = {
                        "AttributeID": attr["a:ObjectID"]
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
