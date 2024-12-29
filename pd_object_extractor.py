import logging

import logging_config
from pd_object_transformer import ObjectTransformer

logger = logging.getLogger(__name__)


class ObjectExtractor:
    def __init__(self, pd_content):
        self.content = pd_content
        self.transformer = ObjectTransformer()
        self.content = self.transformer.convert_timestamps(pd_content=self.content)
        self.dict_domains = self.__domains()

    def models(self) -> list:
        dict_model_internal = self.__model_internal()
        lst_models_external = self.__models_external()
        # Combine models
        lst_models = lst_models_external + [dict_model_internal]
        return lst_models

    def __model_internal(self) -> dict:
        # Model add entity data
        lst_entity = self.__entities_internal()
        if isinstance(lst_entity, dict):
            lst_entity = [lst_entity]
        model = self.content["c:GenerationOrigins"]["o:Shortcut"]  # Document model
        model = self.transformer.clean_keys(model)
        model["IsDocumentModel"] = True
        model["Entities"] = lst_entity
        model["Relationships"] = self.__relationships()
        return model

    def __entities_internal(self) -> list:
        lst_entity = self.content["c:Entities"]["o:Entity"]
        self.transformer.entities_internal(lst_entity, dict_domains=self.dict_domains)
        return lst_entity

    def __models_external(self) -> list:
        # External models
        lst_models_external = self.content["c:SourceModels"][
            "o:Shortcut"
        ]  # External models
        for i in range(len(lst_models_external)):
            new_model = lst_models_external[i]
            new_model["IsDocumentModel"] = False
            lst_models_external[i] = new_model

        # External model entity data
        dict_entities_external = self.__entities_external()

        # Assign entities to intermediate 'target models' for external models
        lst_target_model = self.content["c:TargetModels"]["o:TargetModel"]
        dict_target_models = {}
        for i in range(len(lst_target_model)):
            shortcuts = lst_target_model[i]["c:SessionShortcuts"]["o:Shortcut"]
            if isinstance(shortcuts, dict):
                shortcuts = [shortcuts]
            shortcuts = [i["@Ref"] for i in shortcuts]
            # Add external entity data
            shortcuts_objects = [
                dict_entities_external[i]
                for i in shortcuts
                if i in dict_entities_external.keys()
            ]
            if len(shortcuts_objects) > 0:
                dict_target_models[lst_target_model[i]["a:TargetModelID"]] = {
                    "Entities": shortcuts_objects
                }

        # Assign entity data from 'target models' to external models
        for i in range(len(lst_models_external)):
            new_model = lst_models_external[i]
            new_model = self.transformer.clean_keys(new_model)
            new_model["Entities"] = dict_target_models[new_model["TargetID"]][
                "Entities"
            ]
            lst_models_external[i] = new_model

        return lst_models_external

    def __entities_external(self) -> dict:
        # External model entity data
        dict_result = {}
        lst_entities = self.content["c:Entities"]["o:Shortcut"]
        if isinstance(lst_entities, dict):
            lst_entities = [lst_entities]
        lst_entities = self.transformer.entities_external(lst_entities=lst_entities)
        for entity in lst_entities:
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

    def __relationships(self) -> list:
        lst_relationships = []
        lst_pd_relationships = self.content["c:Relationships"]["o:Relationship"]
        if isinstance(lst_pd_relationships, dict):
            lst_pd_relationships = [lst_pd_relationships]
        for relationship in lst_pd_relationships:
            # Simplify structure
            for object in [
                {"old": "c:Object1", "new": "Object1"},
                {"old": "c:Object2", "new": "Object2"},
            ]:
                relationship[object["new"]] = {}
                attributes = relationship["c:Joins"]["o:RelationshipJoin"][
                    object["old"]
                ]["o:EntityAttribute"]
                if isinstance(attributes, dict):
                    attributes = [attributes]
                attributes = [d["@Ref"] for d in attributes]
                relationship[object["new"]] = {
                    "Id": relationship[object["old"]]["o:Entity"]["@Ref"],
                    "Attributes": attributes,
                }
                relationship.pop(object["old"])
                # TODO: Clean parentidentifier

            relationship.pop("c:Joins")

            # Add to final result
            lst_relationships.append(relationship)
        return lst_relationships

    def mappings(self, lst_entities: list, lst_attributes: list) -> list:
        lst_mappings = self.content["c:Mappings"]["o:DefaultObjectMapping"]

        return lst_mappings
