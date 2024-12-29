import json
import logging
from pathlib import Path

import xmltodict

import logging_config
from model_entity import Entity, Shortcut
from model_mapping import Mapping
from model_helpers import Domain, DataSourceModel
from model_object import ModelObject

logger = logging.getLogger(__name__)


class Model:
    """Represents a Power Designer logical data model document"""

    def __init__(self, file_pd_ldm: str):
        """Extracts data from a JSON-ed version of a Power Designer document and turns it into an object representation

        Args:
            file_pd_ldm (str): JSON version of a Power Designer document (.ldm)
        """
        self.file_pd_ldm = file_pd_ldm
        model = self.read_file_model(file_pd_ldm=file_pd_ldm)

        # TODO: Schema handling
        pd_objects = model["c:TargetModels"]["o:TargetModel"]

        # Extract Data sources # TODO: Research role models["c:DataSources"]["o:DefaultDataSource"]
        # pd_objects = [model["c:DataSources"]["o:DefaultDataSource"]]
        # self.dict_datasource_models = self.extract(
        #     type_object="datasource_model", pd_objects=pd_objects
        # )
        # TODO: Research role models["c:SourceModels"]
        # Extract Domain data
        # TODO: Link between attributes and domains
        pd_objects = model["c:Domains"]["o:Domain"]
        self.dict_domains = self.extract(type_object="domain", pd_objects=pd_objects)
        # Extract entities
        pd_objects = model["c:Entities"]["o:Entity"]
        self.dict_entities = self.extract(type_object="entity", pd_objects=pd_objects)
        # Extract shortcuts
        pd_objects = model["c:Entities"]["o:Shortcut"]
        self.dict_shortcuts = self.extract(
            type_object="shortcut", pd_objects=pd_objects
        )
        # TODO: Extract mappings
        pd_objects = model["c:Mappings"]["o:DefaultObjectMapping"]
        self.dict_mappings = self.extract(type_object="mapping", pd_objects=pd_objects)
        # for mapping in self.lst_pd_mappings:
        #     self.lst_mappings.append(
        #         Mapping(mapping, self.dict_entities, self.dict_shortcuts)
        #     )

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

    def extract(self, type_object: str, pd_objects: dict):
        # TODO: Add Docstring
        """Create objects from model file data"""
        dict_result = {}
        for pd_object in pd_objects:
            if type_object == "target_model":
                object = TargetModel(pd_object)
            elif type_object == "datasource_model":
                object = DataSourceModel(pd_object)
            elif type_object == "domain":
                object = Domain(pd_object)
            elif type_object == "entity":
                object = Entity(pd_object)
            elif type_object == "shortcut":
                object = Shortcut(pd_object)
            elif type_object == "mapping":
                object = Mapping(
                    pd_object,
                    dict_entities=self.dict_entities,
                    dict_shortcuts=self.dict_shortcuts,
                )
            else:
                logger.error(f"No extraction method for type '{type_object}'")
            dict_result[object.id] = object
        return dict_result

    def save_objects_json(self, type_object: str):
        """Save a list of model objects as a JSON file

        Args:
            type_object (str): The type of model objects requested
        """
        # Automatic file name generation
        file_json = Path(Path(self.file_pd_ldm).name).stem
        file_json = f"output/{file_json}_{type_object}.json"
        directory = Path("output")
        directory.mkdir(parents=True, exist_ok=True)
        # Extract and dump dictionaries
        lst_objects = self.get_objects_dict(type_object=type_object)
        with open(file_json, "w") as fp:
            json.dump(lst_objects, fp, indent=4)

    def get_objects_dict(self, type_object: str) -> list:
        """Retrieve list of dictionaries of model objects

        Args:
            type_object (str): The type of model objects requested

        Returns:
            list: List of dictionaries
        """
        dict_result = []
        if type_object == "datasource_models":
            dict_result = [
                item.as_dict() for item in list(self.dict_datasource_models.values())
            ]
        elif type_object == "domain":
            dict_result = [item.as_dict() for item in list(self.dict_domains.values())]
        elif type_object == "entity":
            dict_result = [item.as_dict() for item in list(self.dict_entities.values())]
        elif type_object == "shortcut":
            dict_result = [
                item.as_dict() for item in list(self.dict_shortcuts.values())
            ]
        else:
            logger.error(f"Cannot create objects of unknown type '{type_object}'")
        return dict_result





if __name__ == "__main__":
    file_model = "input/ExampleDWH.ldm"
    model = Model(file_pd_ldm=file_model)
    # Saving model objects
    model.save_objects_json(type_object="datasource_models")
    model.save_objects_json(type_object="shortcut")
    model.save_objects_json(type_object="entity")
    model.save_objects_json(type_object="domain")

    print("Done")
