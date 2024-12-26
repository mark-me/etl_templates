import logging

import logging_config
from model_object import ModelObject

logger = logging.getLogger(__name__)


class Mapping(ModelObject):
    """Extraction process specification: how is the entity populated?"""

    def __init__(self, dict_pd: dict, dict_entities: dict, dict_shortcuts: dict):
        super().__init__(dict_pd)
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None
        # Extract target entity
        id_entity = dict_pd["c:Classifier"]["o:Entity"]["@Ref"]
        self.entity_target = dict_entities[id_entity]
        # Extract entity and shortcut sources
        pd_objects = dict_pd["c:SourceClassifiers"]
        self.dict_sources = self.extract_sources(
            pd_objects=pd_objects,
            dict_entities=dict_entities,
            dict_shortcuts=dict_shortcuts,
        )

        # Joins
        pd_objects = dict_pd["c:ExtendedCompositions"]["o:ExtendedComposition"]
        self.dict_compositions = self.extract_compositions(pd_objects=pd_objects)

        # Features
        # Unpack attributes so they can be matched to mapping features
        dict_attributes = {}
        for key in self.dict_sources:
            source_attrs = self.dict_sources[key].as_dict()["attributes"]
            dict_attributes.update({attr["id"]: attr for attr in source_attrs})

        # pd_feature_maps = dict_pd['c:StructuralFeatureMaps']['o:DefaultStructuralFeatureMapping']
        # dict_features = {}
        # for feature in pd_feature_maps:
        #     dict_features[feature["@Id"]] = feature
        # pd_data_source = dict_pd['c:DataSource']
        print("me")

    def extract_sources(
        self, pd_objects: dict, dict_entities: dict, dict_shortcuts: dict
    ) -> dict:
        """Extract sources and fill corresponding object attributes

        Args:
            pd_objects (dict): Part of the Power Designer document concerning mapping
            dict_entities (dict): Dictionary containing previously extracted Entity objects
            dict_shortcuts (dict): Dictionary containing previously extracted Shortcut objects

        Returns:
            dict: _description_
        """
        dict_sources = {}
        lst_source_types = ["o:Entity", "o:Shortcut"]
        # Keep only the source types that exist
        lst_source_types = list(set(lst_source_types).intersection(pd_objects))
        for source_type in lst_source_types:
            pd_sources = pd_objects[source_type]
            # TODO: Check if can be deleted if len(pd_sources) > 0:
            if isinstance(pd_sources, dict):
                pd_sources = [pd_sources]
            for source in pd_sources:
                source_id = source["@Ref"]
                if source_type == "o:Entity":
                    dict_sources[source_id] = dict_entities[source_id]
                elif source_type == "o:Shortcut":
                    dict_sources[source_id] = dict_shortcuts[source_id]
        return dict_sources

    def extract_compositions(self, pd_objects: dict) -> dict:
        """Determine how sources are used to fill the target entity

        Args:
            pd_objects (dict): _description_

        Returns:
            dict: _description_
        """
        # TODO: Union fills
        dict_compositions = {}
        if isinstance(pd_objects, dict):
            pd_objects = [pd_objects]
        for object in pd_objects:
            composition = MappingComposition(
                dict_pd=object, dict_sources=self.dict_sources
            )
            dict_compositions[composition.id] = composition
        return dict_compositions


class MappingComposition(ModelObject):
    """Specification of the horizontal lineage"""

    def __init__(self, dict_pd, dict_sources: dict):
        super().__init__(dict_pd)
        self.dict_sources = dict_sources
        pd_joins = dict_pd["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
        self.dict_clauses = {}
        if isinstance(pd_joins, dict):
            pd_joins = [pd_joins]

        for join in pd_joins:
            clause = MappingCompositionClause(dict_pd=join, dict_sources=dict_sources)
            self.dict_clauses[clause.id] = clause


class MappingCompositionClause(ModelObject):
    """Represents how Entities or Shortcuts should be used when combining them (FROM, types of JOINS)"""

    def __init__(self, dict_pd: dict, dict_sources: dict):
        super().__init__(dict_pd)
        self.dict_sources = dict_sources
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None
        # Creating an alias
        self.alias = self.name + "_" + self.id
        if "a:ExtendedAttributesText" in dict_pd:
            self.join_type = self.extract_join_type(dict_pd["a:ExtendedAttributesText"])
        else:
            self.join_type = None
            logger.error(f"No clause found for '{self.name}'")
        logger.debug(f"Composition clause '{self.join_type}' for '{self.name}'")
        if self.join_type != "FROM" and self.join_type is not None:
            lst_on_clauses = self.extract_on_clause(dict_pd)

        print("me")

    def extract_join_type(self, extended_attrs_test: str) -> str:
        """Extracting the FROM or JOIN type clause from a very specific Power Designer attributes

        Args:
            extended_attrs_test (str): ExtendedAttributesText

        Returns:
            str: From or Join type
        """
        str_proceeder = "mdde_JoinType,"
        idx_start = extended_attrs_test.find(str_proceeder) + len(str_proceeder)
        idx_end = extended_attrs_test.find("\n", idx_start)
        idx_end = idx_end if idx_end > -1 else len(extended_attrs_test) + 1
        join_type = extended_attrs_test[idx_start:idx_end]
        idx_start = join_type.find("=") + 1
        join_type = join_type[idx_start:].upper()
        return join_type

    def extract_on_clause(self, dict_pd: dict) -> list:
        id_source = dict_pd["c:ExtendedCollections"]["o:ExtendedCollection"][
            "c:Content"
        ]["o:Entity"]["@Ref"]
        # TODO: Handling shortcuts
        source = self.dict_sources[id_source]
        return [source]


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
            logger.error("MappingFeature list of sources not implemented")
