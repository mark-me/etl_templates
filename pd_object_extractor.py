import logging

import logging_config
from pd_object_cleaner import ObjectCleaner

class ObjectExtractor:
    def __init__(self, pd_content):
        self.content = pd_content
        self.cleaner = ObjectCleaner()
        self.content = self.cleaner.convert_timestamps(pd_content=self.content)

    def extract_model_data(self) -> list:
        dict_model_internal = self.extract_model_internal()
        lst_models_external = self.extract_models_external()
        # Combine models
        lst_models = lst_models_external + [dict_model_internal]
        return lst_models

    def extract_model_internal(self) -> dict:
        # Model add entity data
        lst_entity = self.extract_entities_internal()
        if isinstance(lst_entity, dict):
            lst_entity = [lst_entity]
        model = self.content["c:GenerationOrigins"]["o:Shortcut"]  # Document model
        model["IsDocumentModel"] = True
        model["Entities"] = lst_entity
        model["Relationships"] = self.extract_relationship_data()

    def extract_entities_internal(self) -> list:
        lst_entity = self.content["c:Entities"]["o:Entity"]
        self.cleaner.entity_internal(lst_entity)
        return lst_entity

    def extract_models_external(self) -> list:
        # External models
        lst_models_external = self.content["c:SourceModels"][
            "o:Shortcut"
        ]  # External models
        for i in range(len(lst_models_external)):
            new_model = lst_models_external[i]
            new_model["IsDocumentModel"] = False
            lst_models_external[i] = new_model

        # External model entity data
        dict_entities_external = self.extract_entities_external()

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
            new_model["Entities"] = dict_target_models[new_model["a:TargetID"]][
                "Entities"
            ]
            lst_models_external[i] = new_model

        return lst_models_external

    def extract_entities_external(self) -> dict:
        # External model entity data
        dict_result = {}
        lst_entity_external = self.content["c:Entities"]["o:Shortcut"]
        if isinstance(lst_entity_external, dict):
            lst_entity_external = [lst_entity_external]
        for entity_external in lst_entity_external:
            dict_result[entity_external["@Id"]] = entity_external
        return dict_result

    def extract_domain_data(self) -> list:
        lst_domains = []
        if isinstance(lst_domains, dict):
            lst_domains = [lst_domains]

    def extract_relationship_data(self) -> list:
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
