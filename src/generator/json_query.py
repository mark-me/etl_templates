import json
import os
import sys

sys.path.append(os.getcwd())

from src.log_config.logging_config import logging

logger = logging.getLogger(__name__)

class PDDocumentQuery:
    """Stores the models and mappings within a single PDDocument"""

    def __init__(self, file_json: str):
        """Retrieves a list of all models and a list of all mappings within a single PDDocument

        Args:
            document (PDDocument): The representation of a Power Designer logical data model
        """
        # FIXME: Add handling in case file doesn't exist
        with open(file_json) as f:
            self._document = json.load(f)
        self._lst_models = []
        self._lst_mappings = []

    def get_entities(self, name_model: str = None):
        """Retrieves the given name_model's entities or all entities of models
        Args:
            name_model (str): Name of the model

        Returns:
            Array: Each row represents a single entity within a model
        """
        lst_models = self.__get_models()
        lst_results = []
        if name_model is None:
            lst_results = [model["Entities"] for model in lst_models]
        else:
            lst_results = [
                model["Entities"] for model in lst_models if model["Name"] == name_model
            ]
        return lst_results

    def __get_models(self):
        if len(self._lst_models) == 0:
            self._lst_models = self._document["Models"]
        return self._lst_models

    def __get_mapping(self):
        if len(self._lst_mappings) == 0:
            self._lst_mappings = self._document["Mappings"]
        return self._lst_mappings

    def get_MDDE_model(self) -> list:
        """Retrieves all models from lst_models and returns them in a dictionary

        Returns:
            lst_result (dict): Each dictionary value represents a model
        """
        # TODO: Genereren ID's op hash
        lst_models = self.__get_models()
        lst_result = []
        for model in lst_models:
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
        """Retrieves a dictionary of all entities within the models stored in lst_models

        Returns:
            lst_results (dict): Each dictionary value represents an entity
        """
        # TODO: Genereren ID's op hash
        lst_results = []
        lst_models = self.__get_models()
        for model in lst_models:
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
        """**Not yet finished** Retrieves all the attributeID's from all models that have IsDocumentModel = True

        Returns:
            list: Each value represents the ObjectID of a single Attribute
        """
        # TODO: Genereren ID's op hash
        # TODO: Complete
        lst_results = []
        lst_models = self.__get_models()
        # Only the attributes of the non-source model should be deployed
        models_document = [model for model in lst_models if model["IsDocumentModel"]]
        for model in models_document:
            lst_entities = model["Entities"]
            for entity in lst_entities:
                lst_attributes = entity["Attributes"]
                for attr in lst_attributes:
                    dict_selection = {"AttributeID": attr["ObjectID"]}
                    lst_results.append(dict_selection)

        return lst_results
