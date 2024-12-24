import json
import logging

import logging_config

logger = logging.getLogger(__name__)

class ModelObjects:
    def __init__(self, dict_pd: dict):
        self.id = dict_pd["@Id"]
        self.name = dict_pd["a:Name"]
        logger.info(type(self).__name__ + ": " + self.name)
        self.code = dict_pd["a:Code"]


class SourceModel(ModelObjects):
    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.stereotype_target = dict_pd[" a:TargetStereotype"]
        self.id_target = dict_pd["a:TargetID"]
        self.id_class_target = dict_pd["a:TargetClassID"]


class Domain(ModelObjects):
    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.datatype = dict_pd["a:DataType"]
        if "a:Length" in dict_pd:
            self.length = dict_pd["a:Length"]
        else:
            self.length = None
        if "a:Precision" in dict_pd:
            self.precision = dict_pd["a:Precision"]
        else:
            self.precision = None


class Attribute(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        self.id_table = dict_pd["id_table"]
        self.name_table = dict_pd["name_table"]
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None
        self.datatype = dict_pd["a:DataType"]
        if "a:LogicalAttribute.Mandatory" in dict_pd:
            if dict_pd["a:LogicalAttribute.Mandatory"] == 1:
                self.mandatory = True
            else:
                self.mandatory = False
        else:
            self.mandatory = False


class Entity(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        # Setting attributes
        pd_attributes = dict_pd["c:Attributes"]["o:EntityAttribute"]
        self.dict_attributes = {}
        if isinstance(pd_attributes, list):
            for pd_attribute in pd_attributes:
                pd_attribute["id_table"] = self.id
                pd_attribute["name_table"] = self.name
                attribute = Attribute(pd_attribute)

                self.dict_attributes[attribute.id] = attribute
        elif isinstance(pd_attributes, dict):
            pd_attributes["id_table"] = self.id
            pd_attributes["name_table"] = self.name
            attribute = Attribute(pd_attributes)
            self.dict_attributes[attribute.id] = attribute


class ShortcutAttributes(ModelObjects):
    def __init__(self, dict_pd):
        super().__init__(dict_pd)


class Shortcut(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        # Setting attributes
        if "c:SubShortcuts" in dict_pd:
            pd_attributes = dict_pd["c:SubShortcuts"]["o:Shortcut"]
            self.dict_attributes = {}
            if isinstance(pd_attributes, list):
                for pd_attribute in pd_attributes:
                    attribute = ShortcutAttributes(pd_attribute)
                    self.dict_attributes[attribute.id] = attribute
            elif isinstance(pd_attributes, dict):
                attribute = ShortcutAttributes(pd_attribute)
                self.dict_attributes[attribute.id] = attribute


class MappingFeature:
    def __init__(self, dict_pd: dict, dict_features: dict, dict_shortcuts: dict):
        self.id = dict_pd["@Id"]
        self.extended_collection = dict_pd["c:ExtendedCollections"]

        source_features_pd = dict_pd["c:SourceFeatures"]
        self.entity_source = {}
        self.shortcut_source = {}
        if isinstance(source_features_pd, dict):
            if "o:Shortcut" in source_features_pd:
                id_shortcut = source_features_pd["o:Shortcut"]["@Ref"]
                self.shortcut_source[id_shortcut] = dict_shortcuts[id_shortcut]
            if "o:Entity" in source_features_pd:
                id_shortcut = source_features_pd["o:Entity"]["@Ref"]
                self.shortcut_source[id_shortcut] = dict_shortcuts[id_shortcut]
        if isinstance(source_features_pd, list):
            print("List of sources")


class Mapping(ModelObjects):
    def __init__(self, dict_pd: dict, dict_entities: dict, dict_shortcuts: dict):
        super().__init__(dict_pd)
        print("Mapping: " + self.name)
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None

        # Target entity
        id_entity = dict_pd["c:Classifier"]["o:Entity"]["@Ref"]
        self.entity_target = dict_entities[id_entity]

        # Entity sources
        self.entity_sources = {}
        lst_id_entity = [
            sub["@Ref"] for sub in dict_pd["c:SourceClassifiers"]["o:Entity"]
        ]
        for id_entity in lst_id_entity:
            self.entity_sources[id_entity] = dict_entities[id_entity]

        # Features
        pd_features = dict_pd["c:StructuralFeatureMaps"][
            "o:DefaultStructuralFeatureMapping"
        ]
        self.lst_features = []
        for pd_feature in pd_features:
            self.lst_features.append(
                MappingFeature(pd_feature, dict_shortcuts=dict_shortcuts)
            )

        test = "me"


def load_model(file_model: str):
    with open(file_model) as json_file:
        models = json.load(json_file)

    lst_pd_datasources = models["c:DataSources"]

    lst_pd_sourcemodels = ["c:SourceModels"]

    lst_pd_shortcut = models["c:Entities"]["o:Shortcut"]
    with open("output/lst_pd_shortcut.json", "w") as fp:
        json.dump(lst_pd_shortcut, fp, indent=4)

    # lst_mappings = models["c:Mappings"]
    # with open("output/lst_mappings.json", "w") as fp:
    #     json.dump(lst_mappings, fp, indent=4)

    lst_pd_domains = models["c:Domains"]["o:Domain"]
    dict_domains = {}
    for pd_domain in lst_pd_domains:
        domain = Domain(pd_domain)
        dict_domains[domain.id] = domain

    lst_pd_entity = models["c:Entities"]["o:Entity"]
    dict_entities = {}
    for pd_entity in lst_pd_entity:
        # Extract usable entity
        entity = Entity(pd_entity)
        dict_entities[entity.id] = entity

    lst_pd_shortcuts = models["c:Entities"]["o:Shortcut"]
    dict_shortcuts = {}
    for pd_shortcut in lst_pd_shortcuts:
        shortcut = Shortcut(pd_shortcut)
        dict_shortcuts[shortcut.id] = shortcut

    lst_pd_mappings = models["c:Mappings"]["o:DefaultObjectMapping"]
    lst_mappings = []
    for mapping in lst_pd_mappings:
        lst_mappings.append(
            Mapping(mapping, dict_entities, dict_shortcuts=dict_shortcuts)
        )
        lst_mappings.append(
            Mapping(mapping, dict_entities=dict_entities, dict_shortcuts=dict_shortcuts)
        )


if __name__ == "__main__":
    load_model(file_model="output/example_dwh.json")
    print("Done")
