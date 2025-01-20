import logging

import logging_config
from pd_transform_model_internal import TransformModelInternal
from pd_transform_models_external import TransformModelsExternal
from pd_transform_mappings import TransformMappings

logger = logging.getLogger(__name__)


class ObjectExtractor:
    """Collection of functions used to extract the relevant objects from a Power Designer logical data model document"""

    def __init__(self, pd_content):
        self.content = pd_content
        self.transform_model_internal = TransformModelInternal()
        self.transform_models_external = TransformModelsExternal()
        self.transform_mappings = TransformMappings()
        self.dict_domains = self.__domains()

    def models(self) -> list:
        """Retrieves all models and their corresponding objects used in the PowerDesigner document

        Returns:
            list: List of internal model and external models
        """
        dict_model_internal = self.__model_internal()
        lst_models_external = self.__models_external()
        # dict_model_physical = self.__models_physical()
        # Combine models
        lst_models = lst_models_external + [dict_model_internal] #+ [dict_model_physical]
        return lst_models

    def __model_internal(self) -> dict:
        """Retrieves the data on the model which is maintained in the loaded Power Designer document

        Returns:
            dict: All the model's data
        """
        model = self.transform_model_internal.model(content=self.content)
        # Model add entity data
        lst_entity = self.__entities_internal()
        if isinstance(lst_entity, dict):
            lst_entity = [lst_entity]
        model["Entities"] = lst_entity
        model["Relationships"] = self.__relationships(lst_entity=lst_entity)
        return model

    def __entities_internal(self) -> list:
        """Returns all entities of the Power Designer document's model with their attributes and identifiers

        Returns:
            list: Entities
        """
        lst_entity = self.content["c:Entities"]["o:Entity"]
        self.transform_model_internal.entities(lst_entity, dict_domains=self.dict_domains)
        return lst_entity

    def __models_external(self) -> list:
        """Retrieve data on models that are maintained outside of the loaded
        Power Designer document and are used for horizontal lineage

        Returns:
            list: List of external models with all their corresponding elements
        """
        # The models will be derived by looking up the TargetModels associated with the entity shortcuts
        # External entity (shortcut) data
        dict_entities = self.__entities_external()
        # Retain 'TargetModels' have references to entities
        lst_target_model = self.content["c:TargetModels"]["o:TargetModel"]
        lst_models = self.transform_models_external.models(
            lst_models=lst_target_model, dict_entities=dict_entities
        )
        return lst_models

    def __entities_external(self) -> dict:
        """Retrieve the Entities of the external model and their associated entities

        Returns:
            dict: A dict of Entities, where each key contains data on an Entity and their attributes as a value
        """
        # External model entity data
        dict_result = {}
        lst_entities = self.content["c:Entities"]["o:Shortcut"]
        if isinstance(lst_entities, dict):
            lst_entities = [lst_entities]
        lst_entities = self.transform_models_external.entities(lst_entities=lst_entities)
        for entity in lst_entities:
            logger.debug(f"Found external entity shortcut for '{entity['Name']}'")
            dict_result[entity["Id"]] = entity
        return dict_result

    def __domains(self) -> dict:
        dict_domains = {}
        lst_domains = self.content["c:Domains"]["o:Domain"]
        dict_domains = self.transform_model_internal.domains(lst_domains=lst_domains)
        return dict_domains

    def __relationships(self, lst_entity: list) -> list:
        lst_relationships = []
        if "c:Relationships" in self.content:
            lst_pd_relationships = self.content["c:Relationships"]["o:Relationship"]
            lst_relationships = self.transform_model_internal.relationships(
                lst_relationships=lst_pd_relationships, lst_entity=lst_entity
            )
        return lst_relationships

    def mappings(self, dict_entities: list, dict_attributes: list) -> list:
        lst_mappings = self.content["c:Mappings"]["o:DefaultObjectMapping"]
        lst_mappings = self.transform_mappings.mappings(
            lst_mappings=lst_mappings,
            dict_entities=dict_entities,
            dict_attributes=dict_attributes,
        )
        return lst_mappings
