import json
import logging

import logging_config

logger = logging.getLogger(__name__)


class Model:
    def __init__(self, file_pd_ldm: str):
        self.file_pd_ldm = file_pd_ldm
        with open(file_pd_ldm) as json_file:
            models = json.load(json_file)

        self.lst_pd_datasources = models["c:DataSources"]
        self.lst_pd_source_models = ["c:SourceModels"]
        self.lst_pd_mappings = models["c:Mappings"]["o:DefaultObjectMapping"]

        self.dict_domains = self.extract(models["c:Domains"]["o:Domain"], type_object = "domain")
        self.dict_entities = self.extract(models["c:Entities"]["o:Entity"], type_object = "entity")
        self.dict_shortcuts = self.extract(models["c:Entities"]["o:Shortcut"], type_object="shortcut")

        self.lst_mappings = []
        for mapping in self.lst_pd_mappings:
            self.lst_mappings.append(
                Mapping(mapping, self.dict_entities, self.dict_shortcuts)
            )
            self.lst_mappings.append(
                Mapping(mapping, self.dict_entities, self.dict_shortcuts)
            )

    def extract(self, pd_objects: dict, type_object: str):
        dict_result = {}
        for pd_object in pd_objects:
            if type_object == "domain":
                object = Domain(pd_object)
            elif type_object == "entity":
                object = Entity(pd_object)
            elif type_object == "shortcut":
                object = Shortcut(pd_object)
            dict_result[object.id] = object
        return dict_result


class ModelObjects:
    """Abstract class to fill all common denominators from PowerDesigner
    * id = Identifier
    * name = Name
    * code = Name?
    """

    def __init__(self, dict_pd: dict):
        self.id = dict_pd["@Id"]
        self.name = dict_pd["a:Name"]
        logger.info(type(self).__name__ + ": " + self.name)
        self.code = dict_pd["a:Code"]


class SourceModel(ModelObjects):
    """No clue"""

    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.stereotype_target = dict_pd[" a:TargetStereotype"]
        self.id_target = dict_pd["a:TargetID"]
        self.id_class_target = dict_pd["a:TargetClassID"]


class Domain(ModelObjects):
    """Datatypes to be applied to attributes"""

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
    """Entity attributes"""

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
    """Entities"""

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
    """Attributes of shortcuts"""

    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.id_shortcut = dict_pd["id_shortcut"]
        self.name_shortcut = dict_pd["name_shortcut"]


class Shortcut(ModelObjects):
    """An entity that is not part of the current model"""

    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        self.dict_attributes = {}
        # Setting attributes
        if "c:SubShortcuts" in dict_pd:
            pd_attributes = dict_pd["c:SubShortcuts"]["o:Shortcut"]
            if isinstance(pd_attributes, list):
                for pd_attribute in pd_attributes:
                    pd_attribute["id_shortcut"] = self.id
                    pd_attribute["name_shortcut"] = self.name
                    attribute = ShortcutAttributes(pd_attribute)
                    self.dict_attributes[attribute.id] = attribute
            elif isinstance(pd_attributes, dict):
                pd_attribute["id_shortcut"] = self.id
                pd_attribute["name_shortcut"] = self.name
                attribute = ShortcutAttributes(pd_attribute)
                self.dict_attributes[attribute.id] = attribute
        else:
            logger.error("Shortcut '" + self.name + "' has no attributes")


class MappingFeature:
    """Extraction process specification: how is the attribute populated?"""

    def __init__(self, dict_pd: dict, dict_attributes: dict):
        self.id = dict_pd["@Id"]
        self.extended_collection = dict_pd["c:ExtendedCollections"]

        source_features_pd = dict_pd["c:SourceFeatures"]
        self.entity_source = {}
        self.shortcut_source = {}
        if isinstance(source_features_pd, dict):
            if "o:Shortcut" in source_features_pd:
                id_shortcut = source_features_pd["o:Shortcut"]["@Ref"]
                self.shortcut_source[id_shortcut] = dict_attributes[id_shortcut]
            if "o:Entity" in source_features_pd:
                id_shortcut = source_features_pd["o:Entity"]["@Ref"]
                self.shortcut_source[id_shortcut] = dict_attributes[id_shortcut]
        elif isinstance(source_features_pd, list):
            logger.error("MappingFeature list of sources")


class Mapping(ModelObjects):
    """Extraction process specification: how is the entity populated?"""

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
        # Derive entity and shortcut sources
        lst_source_ids = self.extract_source_ids(dict_pd=dict_pd)
        self.entity_sources = {}
        for id_source in lst_source_ids:
            if id_source in dict_entities:
                self.entity_sources[id_source] = dict_entities[id_source]
            elif id_source in dict_shortcuts:
                self.entity_sources[id_source] = dict_shortcuts[id_source]
            else:
                logger.error("Source entity or shortcut not found for " + id_source)

        # Features
        # Unpack attributes so they can be matched to mapping features
        lst_attrs = [
            value.dict_attributes for key, value in self.entity_sources.items()
        ]
        dict_attrs = {k: v for e in lst_attrs for (k, v) in e.items()}

        pd_features = dict_pd["c:StructuralFeatureMaps"][
            "o:DefaultStructuralFeatureMapping"
        ]
        self.lst_features = []
        for pd_feature in pd_features:
            self.lst_features.append(
                MappingFeature(pd_feature, dict_attributes=dict_attrs)
            )

    def find_entity_sources(self, dict_pd: dict, dict_entities: dict) -> dict:
        entity_sources = {}
        if "o:Entity" in dict_pd["c:SourceClassifiers"]:
            pd_entities = dict_pd["c:SourceClassifiers"]["o:Entity"]
            if len(pd_entities) > 0:
                if isinstance(pd_entities, list):
                    lst_id_entity = [sub["@Ref"] for sub in pd_entities]
                    for id_entity in lst_id_entity:
                        entity_sources[id_entity] = dict_entities[id_entity]
                elif isinstance(pd_entities, dict):
                    entity_sources[id_entity] = dict_entities[id_entity]
        return entity_sources

    def find_shortcut_sources(self, dict_pd: dict, dict_shortcuts: dict) -> dict:
        shortcut_sources = {}
        if "o:Shortcut" in dict_pd["c:SourceClassifiers"]:
            pd_shortcuts = dict_pd["c:SourceClassifiers"]["o:Shortcut"]
            if len(pd_shortcuts) > 0:
                if isinstance(pd_shortcuts, list):
                    for id_shortcut in pd_shortcuts:
                        shortcut_sources[id_shortcut] = dict_shortcuts[id_shortcut]
                elif isinstance(pd_shortcuts, dict):
                    id_shortcut = pd_shortcuts["@Ref"]
                    shortcut_sources[id_shortcut] = dict_shortcuts[id_shortcut]
        return shortcut_sources

    def extract_source_ids(self, dict_pd: dict) -> list:
        lst_source_ids = []
        pd_classifiers = dict_pd["c:SourceClassifiers"]
        lst_source_types = ["o:Entity", "o:Shortcut"]
        for source_type in lst_source_types:
            if source_type in pd_classifiers:
                pd_sources = pd_classifiers[source_type]
                if len(pd_sources) > 0:
                    if isinstance(pd_sources, list):
                        lst_source_ids = lst_source_ids + [sub["@Ref"] for sub in pd_sources]
                    elif isinstance(pd_sources, dict):
                        lst_source_ids = lst_source_ids + [pd_sources["@Ref"]]
        return lst_source_ids


def load_model(file_model: str):
    model = Model(file_pd_ldm=file_model)


if __name__ == "__main__":
    load_model(file_model="output/example_dwh.json")
    print("Done")
