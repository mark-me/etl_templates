import logging

import logging_config
from pd_object_transformer import ObjectTransformer

logger = logging.getLogger(__name__)


class ObjectExtractor:
    """Collection of functions used to extract the relevant objects from a Power Designer logical datamodel document"""

    def __init__(self, pd_content):
        self.content = pd_content
        self.transformer = ObjectTransformer()
        self.content = self.transformer.convert_timestamps(pd_content=self.content)
        self.dict_domains = self.__domains()

    def models(self) -> list:
        """Retrieves all models and their corresponding objects used in the PowerDesigner document

        Returns:
            list: List of internal model and external models
        """
        dict_model_internal = self.__model_internal()
        lst_models_external = self.__models_external()
        # Combine models
        lst_models = lst_models_external + [dict_model_internal]
        return lst_models

    def __model_internal(self) -> dict:
        """Retrieves the data on the model which is maintained in the loaded Power Designer document

        Returns:
            dict: All the model's data
        """
        # Model add entity data
        lst_entity = self.__entities_internal()
        if isinstance(lst_entity, dict):
            lst_entity = [lst_entity]
        if "c:GenerationOrigins" in self.content:
            model = self.content["c:GenerationOrigins"]["o:Shortcut"]  # Document model
            model = self.transformer.clean_keys(model)
        else:
            lst_include = [
                "@Id",
                "@a:ObjectID",
                "a:Name",
                "a:Code",
                "a:CreationDate",
                "a:Creator",
                "a:ModificationDate",
                "a:Modifier",
                "a:PackageOptionsText",
                "a:ModelOptionsText",
                "a:Author",
                "a:Version",
                "a:RepositoryFilename",
                "a:ExtendedAttributesText",
            ]
            model = {
                item: self.content[item] for item in self.content if item in lst_include
            }
            model = self.transformer.clean_keys(model)
        model["IsDocumentModel"] = True
        model["Entities"] = lst_entity
        model["Relationships"] = self.__relationships(lst_entity=lst_entity)
        return model

    def __entities_internal(self) -> list:
        """Returns all entities of the Power Designer document's model with their attributes and identifiers

        Returns:
            list: Entities
        """
        lst_entity = self.content["c:Entities"]["o:Entity"]
        self.transformer.entities_internal(lst_entity, dict_domains=self.dict_domains)
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
        lst_models = self.transformer.models_external(
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
        lst_entities = self.transformer.entities_external(lst_entities=lst_entities)
        for entity in lst_entities:
            logger.debug(f"Found exteral entity shortcut for '{entity["Name"]}'")
            dict_result[entity["Id"]] = entity
        return dict_result

    def __domains(self) -> dict:
        dict_domains = {}
        lst_domains = self.content["c:Domains"]["o:Domain"]
        if isinstance(lst_domains, dict):
            lst_domains = [lst_domains]
        lst_domains = self.transformer.clean_keys(lst_domains)
        for domain in lst_domains:
            dict_domains[domain["Id"]] = domain
        return dict_domains

    def __relationships(self, lst_entity: list) -> list:
        lst_relationships = []
        if "c:Relationships" in self.content:
            lst_pd_relationships = self.content["c:Relationships"]["o:Relationship"]
            lst_relationships = self.transformer.relationships(
                lst_relationships=lst_pd_relationships, lst_entity=lst_entity
            )
        return lst_relationships

    def mappings(self, dict_entities: list, dict_attributes: list) -> list:
        lst_mappings = self.content["c:Mappings"]["o:DefaultObjectMapping"]
        lst_mappings = self.transformer.mappings(
            lst_mappings=lst_mappings,
            dict_entities=dict_entities,
            dict_attributes=dict_attributes,
        )
        return lst_mappings
