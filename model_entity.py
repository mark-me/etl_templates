import logging

import logging_config
from model_object import ModelObject

logger = logging.getLogger(__name__)


class Entity(ModelObject):
    """Entities"""

    def __init__(self, dict_pd: dict):
        """Generates an Entity object

        Args:
            dict_pd (dict): Relevant part of the Power Designer document
        """
        super().__init__(dict_pd)
        # Setting attributes
        pd_attributes = dict_pd["c:Attributes"]["o:EntityAttribute"]
        self.dict_attributes = self.extract_attributes(pd_attributes)

    def extract_attributes(self, pd_objects: dict) -> dict:
        """Extract Power Designer entity attributes and turn them into objects

        Args:
            pd_objects (dict): Relevant part of Power Designer file

        Returns:
            dict: Contains the Entity Attribute objects
        """
        dict_attributes = {}
        if len(pd_objects) > 0:
            if isinstance(pd_objects, dict):
                pd_objects = [pd_objects]
            for pd_attribute in pd_objects:
                pd_attribute["id_parent"] = self.id
                pd_attribute["name_parent"] = self.name
                attribute = EntityAttribute(pd_attribute)
                dict_attributes[attribute.id] = attribute
        else:
            logger.error(f"Table '{self.name}' has no attributes")


        return dict_attributes

    def as_dict(self) -> dict:
        """Uses the class data to generate a dictionary

        Returns:
            dict: Contains Shortcut data
        """
        dict_result = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type_object": "entity",
        }
        dict_result["attributes"] = [
            item.__dict__ for item in list(self.dict_attributes.values())
        ]
        return dict_result


class EntityAttribute(ModelObject):
    """Entity attributes"""

    def __init__(self, dict_pd: dict):
        """Generates an Entity's attribute

        Args:
            dict_pd (dict): Part of a PowerDesigner document that specifies an Entity Attribute
        """
        super().__init__(dict_pd)
        self.id_parent = dict_pd["id_parent"]
        self.name_parent = dict_pd["name_parent"]
        self.type_object = "entity_attribute"
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None
        self.datatype = dict_pd["a:DataType"]
        if "a:LogicalAttribute.Mandatory" in dict_pd:
            self.mandatory = dict_pd["a:LogicalAttribute.Mandatory"] == 1
        else:
            self.mandatory = False



class Shortcut(ModelObject):
    """A Shortcut is an entity that is not part of the current model"""

    def __init__(self, dict_pd: dict):
        """Generates a Shortcut object

        Args:
            dict_pd (dict): Part of a PowerDesigner document that specifies a Shortcut
        """
        super().__init__(dict_pd)
        self.dict_attributes = {}
        # Setting attributes
        if "c:SubShortcuts" in dict_pd:
            pd_attributes = dict_pd["c:SubShortcuts"]["o:Shortcut"]
            self.dict_attributes = self.extract_attributes(pd_objects=pd_attributes)
        else:
            logger.error(f"Shortcut '{self.name}' has no attributes")

    def extract_attributes(self, pd_objects: dict) -> dict:
        """Creates a dictionary of objects for the Shortcut's attributes

        Args:
            pd_objects (dict): Part of the Power Designer document that specifies a shortcut's attributes

        Returns:
            dict: A dictionary containing all the shortcut attributes as objects
        """
        dict_attributes = {}
        if len(pd_objects) > 0:
            if isinstance(pd_objects, dict):
                pd_objects = [pd_objects]
            for pd_attribute in pd_objects:
                pd_attribute["id_parent"] = self.id
                pd_attribute["name_parent"] = self.name
                attribute = ShortcutAttribute(pd_attribute)
                dict_attributes[attribute.id] = attribute
        else:
            logger.error(f"Shortcut '{self.name}' has no attributes")
        return dict_attributes

    def as_dict(self) -> dict:
        """Uses the class data to generate a dictionary

        Returns:
            dict: Contains Shortcut data
        """
        dict_result = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "type_object": "shortcut",
        }
        dict_result["attributes"] = [
            item.__dict__ for item in list(self.dict_attributes.values())
        ]
        return dict_result


class ShortcutAttribute(ModelObject):
    """Attribute of a shortcut"""
    def __init__(self, dict_pd):
        """Creates a shortcut attribute object based on Power Designer data

        Args:
            dict_pd (_type_): Part of the Power Designer document that specifies a Shortcut attribute
        """
        super().__init__(dict_pd)
        self.id_parent = dict_pd["id_parent"]
        self.name_parent = dict_pd["name_parent"]
        self.type_object = "shortcut_attribute"
