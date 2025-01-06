import logging

import logging_config
from pd_transform_object import ObjectTransformer

logger = logging.getLogger(__name__)


class TransformModelsExternal(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def models(self, lst_models: list, dict_entities: dict) -> list:
        """Retain 'TargetModels' have references to entities and
        enrich them with those entities

        Args:
            lst_models (list): Data target models
            dict_entities (dict): Contains all external entities

        Returns:
            list: Target models with entity data
        """
        lst_result = []
        lst_models = self.clean_keys(lst_models)
        for model in lst_models:
            # model = self.convert_timestamps(model)
            shortcuts = model["c:SessionShortcuts"]["o:Shortcut"]
            if isinstance(shortcuts, dict):
                shortcuts = [shortcuts]
            shortcuts = [i["@Ref"] for i in shortcuts]
            model["Entities"] = [
                dict_entities[id] for id in shortcuts if id in dict_entities
            ]
            if len(model["Entities"]) > 0:
                model["IsDocumentModel"] = False
                lst_result.append(model)
                model.pop("c:SessionShortcuts")
                model.pop("c:SessionReplications")
                model.pop("c:FullShortcutModel")
        return lst_result

    def entities(self, lst_entities: list) -> list:
        """Reroutes and cleans the Power Designer document data on external entities

        Args:
            lst_entities (list): The part of the Power Designer document that describes external entities

        Returns:
            list: The cleaned up version of the external entities data
        """
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            entity = lst_entities[i]
            if "c:FullShortcutReplica" in entity:
                entity.pop("c:FullShortcutReplica")
            self.__entity_attribute(entity)
            entity.pop("c:SubShortcuts")
            lst_entities[i] = entity
        return lst_entities

    def __entity_attribute(self, entity: dict) -> dict:
        lst_attributes = entity["c:SubShortcuts"]["o:Shortcut"]
        for i in range(len(lst_attributes)):
            attr = lst_attributes[i]
            if "c:FullShortcutReplica" in attr:
                attr.pop("c:FullShortcutReplica")
            attr["Order"] = i
            lst_attributes[i] = attr
        lst_attributes = self.clean_keys(lst_attributes)
        entity["Attributes"] = lst_attributes
        return entity
