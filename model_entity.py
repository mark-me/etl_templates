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
        if "c:Identifiers" in dict_pd:
            pd_identifiers = dict_pd["c:Identifiers"]["o:Identifier"]
            pd_identifier_primary = dict_pd["c:PrimaryIdentifier"]["o:Identifier"]
            self.dict_identifiers = self.extract_identifiers(
                pd_identifiers=pd_identifiers, pd_primary=pd_identifier_primary
            )

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

    def extract_identifiers(self, pd_identifiers: dict, pd_primary: dict) -> dict:
        # Primary identifier
        if isinstance(pd_primary, list):
            logger.error(f"Entity '{self.name}' contains multiple primary identifiers")
        id_primary = pd_primary["@Ref"]

        # Retrieve all identifiers
        dict_identifier = {}
        if isinstance(pd_identifiers, dict):
            pd_identifiers = [pd_identifiers]
        for identifier in pd_identifiers:
            id = EntityIdentifier(
                dict_pd=identifier,
                id_primary=id_primary,
                dict_entity_attrs=self.dict_attributes,
            )
            dict_identifier[id.id] = id
        return dict_identifier

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
        dict_result["identifiers"] = [
            item.__dict__ for item in list(self.dict_identifiers.values())
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


class EntityIdentifier(ModelObject):
    """Set of attributes that identify a subset of the entities"""

    def __init__(self, dict_pd, id_primary: str, dict_entity_attrs: dict):
        super().__init__(dict_pd)
        self.is_primary = self.id == id_primary # Set primary identifier
        # Attributes that are part of the identifier
        self.dict_attributes = {}
        dict_attributes = dict_pd["c:Identifier.Attributes"]["o:EntityAttribute"]
        if isinstance(dict_attributes, dict):
            dict_attributes = [dict_attributes]
        for attribute in dict_attributes:
            id_attribute = attribute["@Ref"]
            self.dict_attributes["id"] = id_attribute
            self.dict_attributes["name_attribute"] = dict_entity_attrs[
                id_attribute
            ].name
            self.dict_attributes["code_attribute"] = dict_entity_attrs[
                id_attribute
            ].code

    def as_dict(self) -> dict:
        """Creates a dictionary of the object's data elements

        Returns:
            dict: Contains object data
        """
        dict_result = {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "is_primary": self.is_primary,
        }
        dict_result["attributes"] = [
            item.__dict__ for item in list(self.dict_attributes.values())
        ]


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
