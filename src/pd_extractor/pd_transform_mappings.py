import datetime  # TDODO: Remove
import json  # TODO: Remove
import logging

import src.log_config.logging_config as logging_config
from pd_transform_object import ObjectTransformer

logger = logging.getLogger(__name__)


class TransformMappings(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def mappings(
        self, lst_mappings: list, dict_entities: dict, dict_attributes: dict
    ) -> list:
        """Reroutes mapping data and enriches it with entity and attribute data

        Args:
            lst_mappings (list): The part of the PowerDesigner document which contains the list of mappings
            dict_entities (dict): All entities in the document (internal and external)
            dict_attributes (dict): All attributes in the document (internal and external)

        Returns:
            list: _description_
        """
        lst_ignored_mapping = [
            "Mapping Br Custom Business Rule Example",
            "Mapping AggrTotalSalesPerCustomer",
            "Mapping Pivot Orders Per Country Per Date",
        ]  # TODO: Ignored mappings for 1st version with CrossBreeze example.
        lst_mappings = [
            m for m in lst_mappings if m["a:Name"] not in lst_ignored_mapping
        ]

        lst_mappings = self.clean_keys(lst_mappings)
        for i in range(len(lst_mappings)):
            mapping = lst_mappings[i]
            logger.debug(
                f"Starting mapping transform for {str(i)}) '{mapping['Name']}'"
            )

            # Target entity rerouting and enriching
            if "o:Entity" in mapping["c:Classifier"]:
                id_entity_target = mapping["c:Classifier"]["o:Entity"]["@Ref"]
                mapping["EntityTarget"] = dict_entities[id_entity_target]
                logger.debug(
                    f"Mapping target entity: '{mapping['EntityTarget']['Name']}'"
                )
                # Source entities rerouting and enriching
                mapping = self.__mapping_entities_source(
                    mapping=mapping, dict_entities=dict_entities
                )
            else:
                logger.warning(f"Mapping without entity found: '{mapping['Name']}'")
            mapping.pop("c:Classifier")

            # Reroute datasource
            # TODO: Research role of DataSource
            mapping["DataSourceID"] = mapping["c:DataSource"]["o:DefaultDataSource"][
                "@Ref"
            ]
            mapping.pop("c:DataSource")

            # Rerouting, restructuring and enriching compositionObjects
            mapping = self.__mapping_compositions(
                mapping=mapping,
                dict_entities=dict_entities,
                dict_attributes=dict_attributes,
            )
            # Mapping attributes
            mapping = self.__mapping_attributes(
                mapping=mapping, dict_attributes=dict_attributes
            )

            lst_mappings[i] = mapping
        return lst_mappings

    def __mapping_attributes(self, mapping: dict, dict_attributes: dict) -> dict:
        """Cleans and enriches data on the mapping of attributes

        Args:
            mapping (dict): The part of the PowerDesigner document that describes a mapping
            dict_attributes (dict): All entities in the document (internal and external)

        Returns:
            dict: Mapping data where the attribute mapping is cleaned
        """
        if "c:StructuralFeatureMaps" in mapping:
            lst_attr_maps = mapping["c:StructuralFeatureMaps"][
                "o:DefaultStructuralFeatureMapping"
            ]
            if isinstance(lst_attr_maps, dict):
                lst_attr_maps = [lst_attr_maps]
            lst_attr_maps = self.clean_keys(lst_attr_maps)
            for i in range(len(lst_attr_maps)):
                attr_map = lst_attr_maps[i]
                # Ordering
                attr_map["Order"] = i
                # Target feature
                id_attr = attr_map["c:BaseStructuralFeatureMapping.Feature"][
                    "o:EntityAttribute"
                ]["@Ref"]
                attr_map["AttributeTarget"] = dict_attributes[id_attr]
                attr_map.pop("c:BaseStructuralFeatureMapping.Feature")
                # Source feature's entity alias
                has_entity_alias = False
                if "c:ExtendedCollections" in attr_map:
                    has_entity_alias = True
                    id_entity_alias = attr_map["c:ExtendedCollections"][
                        "o:ExtendedCollection"
                    ]["c:Content"]["o:ExtendedSubObject"]["@Ref"]
                    attr_map.pop("c:ExtendedCollections")
                # Source attribute
                if "c:SourceFeatures" in attr_map:
                    type_entity = [
                        value
                        for value in ["o:Entity", "o:Shortcut", "o:EntityAttribute"]
                        if value in attr_map["c:SourceFeatures"]
                    ][0]
                    id_attr = attr_map["c:SourceFeatures"][type_entity]["@Ref"]
                    attr_map["AttributesSource"] = dict_attributes[id_attr]
                    if has_entity_alias:
                        attr_map["AttributesSource"]["EntityAlias"] = id_entity_alias
                    attr_map.pop("c:SourceFeatures")

                lst_attr_maps[i] = attr_map
            mapping["AttributeMapping"] = lst_attr_maps
            mapping.pop("c:StructuralFeatureMaps")
        return mapping

    def __mapping_entities_source(self, mapping: dict, dict_entities: dict) -> dict:
        """Cleaning the source entities involved in a mapping

        Args:
            mapping (dict): The part of the PowerDesigner document that describes a mapping
            dict_entities (dict): All entities in the document (internal and external)

        Returns:
            dict: Version of mapping data where source entity data  is cleaned and enriched
        """
        logger.debug(
            f"Starting sources entities transform for mapping '{mapping['Name']}'"
        )
        lst_source_entity = []
        for entity_type in ["o:Entity", "o:Shortcut"]:
            if entity_type in mapping["c:SourceClassifiers"]:
                source_entity = mapping["c:SourceClassifiers"][entity_type]
                if isinstance(source_entity, dict):
                    source_entity = [source_entity]
                source_entity = [d["@Ref"] for d in source_entity]
                lst_source_entity = lst_source_entity + source_entity
        lst_source_entity = [dict_entities[item] for item in lst_source_entity]
        mapping["EntitiesSource"] = lst_source_entity
        mapping.pop("c:SourceClassifiers")
        return mapping

    def __mapping_compositions(
        self, mapping: dict, dict_entities: dict, dict_attributes: dict
    ) -> dict:
        """Cleans the composition of source entities data

        Args:
            mapping (dict): The part of the PowerDesigner document that describes a mapping
            dict_entities (dict): All entities (in- and external)
            dict_attributes (dict): All attributes (in- and external)

        Returns:
            list: Version of mapping data where composition data is cleaned and enriched
        """
        logger.debug(f"Starting compositions transform for mapping '{mapping['Name']}'")
        # TODO Remove writing mapping
        with open("output/mapping_" + mapping["Name"] + ".json", "w") as outfile:
            json.dump(mapping, outfile, indent=4, default=self.__serialize_datetime)

        lst_compositions = mapping["c:ExtendedCompositions"]["o:ExtendedComposition"]
        if isinstance(lst_compositions, dict):
            lst_compositions = [lst_compositions]
        # FIXME: Verwijderen compositions die uit extensie voortkomen 'mdde_Mapping_Examples'
        lst_compositions = self.clean_keys(lst_compositions)
        lst_compositions_new = []
        for i in range(len(lst_compositions)):
            if "ExtendedBaseCollection.CollectionName" in lst_compositions[i]:
                if (
                    lst_compositions[i]["ExtendedBaseCollection.CollectionName"]
                    != "mdde_Mapping_Examples"
                ):
                    lst_compositions_new.append(lst_compositions[i])
            else:
                logger.warning("No 'ExtendedBaseCollection.CollectionName'")
        lst_compositions = lst_compositions_new[0]
        # lst_compositions = lst_compositions_new["c:ExtendedComposition.Content"][
        #     "o:ExtendedSubObject"
        # ]

        # Transform and enrich individual compositions

        # eerste countlist bepaling niet meer nodig indien de if code alle gevallen bevat
        if "c:ExtendedComposition.Content" in lst_compositions:
            countlist = len(
                lst_compositions["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
                )
            if (
                "c:ExtendedCollections"
                in lst_compositions["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
            ):
                countlist = len(
                    lst_compositions["c:ExtendedComposition.Content"][
                        "o:ExtendedSubObject"
                    ]["c:ExtendedCollections"]
                )
            elif "o:ExtendedSubObject" in lst_compositions["c:ExtendedComposition.Content"]:
                countlist = len(
                    lst_compositions["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
                )
            elif (
                "c:ExtendedCollections" in lst_compositions["c:ExtendedComposition.Content"]
            ):
                countlist = len(
                    lst_compositions["c:ExtendedComposition.Content"][
                        "c:ExtendedCollections"
                    ]
                )
            for i in range(countlist):
                if (
                    "c:ExtendedCollections"
                    in lst_compositions["c:ExtendedComposition.Content"][
                        "o:ExtendedSubObject"
                    ]
                ):
                    # composition = self.__composition(
                    #     lst_compositions["c:ExtendedComposition.Content"][
                    #         "o:ExtendedSubObject"
                    #     ][i],
                    composition = self.__composition(
                        lst_compositions["c:ExtendedComposition.Content"][
                            "o:ExtendedSubObject"
                        ]["c:ExtendedCollections"]["o:ExtendedCollection"],
                        dict_entities=dict_entities,
                        dict_attributes=dict_attributes,
                    )
                elif (
                    "o:ExtendedSubObject"
                    in lst_compositions["c:ExtendedComposition.Content"]
                ):
                    composition = self.__composition(
                        lst_compositions["c:ExtendedComposition.Content"][
                            "o:ExtendedSubObject"
                        ][i],
                        dict_entities=dict_entities,
                        dict_attributes=dict_attributes,
                    )
                composition["Order"] = i
                lst_compositions[i] = composition
            lst_compositions.pop("c:ExtendedComposition.Content")
        else:
            logger.warning("Mapping without content")
        mapping["Compositions"] = lst_compositions
        mapping.pop("c:ExtendedCompositions")
        return mapping

    def __composition(
        self, composition: dict, dict_entities: dict, dict_attributes: dict
    ) -> dict:
        composition = self.clean_keys(composition)
        # Determine composition clause (FROM/JOIN)
        if "ExtendedAttributesText" in composition:
            composition["CompositionType"] = self.__extract_value_from_attribute_text(
                composition["ExtendedAttributesText"],
                preceded_by="mdde_JoinType,",
            )
            logger.debug(
                f"Composition {composition['CompositionType']} for '{composition['Name']}'"
            )
        else:
            logger.warning("No 'ExtendedAttributesText")
        # logger.error(
        #     f"Composition '{composition['Name']}' has no ExtendedAttributesText to extract a composition type from."
        # )

        # Determine entities involved
        composition = self.__composition_entity(
            composition=composition, dict_entities=dict_entities
        )
        # Join conditions (ON clause)
        if "c:ExtendedCompositions" in composition:
            if composition["CompositionType"].upper() not in ["APPLY", "FROM"]:
                composition = self.__composition_join_conditions(
                    composition=composition, dict_attributes=dict_attributes
                )
            else:
                composition = self.__composition_apply_conditions(
                    composition=composition, dict_attributes=dict_attributes
                )
        return composition

    def __composition_entity(self, composition: dict, dict_entities: dict) -> dict:
        """Reroutes and enriches a composition with entity data.

        Args:
            composition (dict): Composition data
            dict_entities (dict): All entities (in- and external)

        Returns:
            dict: A cleaned and enriched version of composition data
        """
        logger.debug(
            f"Starting entity transform for composition '{composition['Name']}'"
        )

        if "c:ExtendedComposition.Content" in composition:
            root_data = "c:ExtendedComposition.Content"
            entity = composition["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
        elif "c:ExtendedCollections" in composition:
            root_data = "c:ExtendedCollections"
            entity = composition["c:ExtendedCollections"]["o:ExtendedCollection"]
        elif "c:Content" in composition:
            root_data = "c:Content"
            entity = composition
        else:
            return composition
        entity = self.clean_keys(entity)
        if "c:Content" in entity:
            type_entity = [
                value
                for value in ["o:Entity", "o:Shortcut"]
                if value in entity["c:Content"]
            ][0]
            id_entity = entity["c:Content"][type_entity]["@Ref"]
            entity = dict_entities[id_entity]
            logger.debug(f"Composition entity '{entity['Name']}'")
        composition["Entity"] = entity
        composition["EntityAlias"] = composition["Id"]
        composition.pop(root_data)
        return composition

    def __composition_join_conditions(
        self, composition: dict, dict_attributes: dict
    ) -> dict:
        """Cleans and enriches data of the join conditions of one of the compositions

        Args:
            composition (dict): Composition data
            dict_attributes (dict): All attributes (in- and external)

        Returns:
            dict: A cleaned and enriched version of join condition data
        """
        logger.debug(
            f"Join conditions transform for composition '{composition['Name']}'"
        )
        lst_conditions = composition["c:ExtendedCompositions"]["o:ExtendedComposition"][
            "c:ExtendedComposition.Content"
        ]["o:ExtendedSubObject"]
        if isinstance(lst_conditions, dict):
            lst_conditions = [lst_conditions]
        lst_conditions = self.clean_keys(lst_conditions)

        for i in range(len(lst_conditions)):
            condition = lst_conditions[i]
            condition["Order"] = i
            logger.debug(
                f"Join conditions transform for {str(i)}) '{condition['Name']}'"
            )
            # Condition operator and Parent literal (using a fixed value instead of a parent column)
            condition_operator = "="
            parent_literal = None
            if "ExtendedAttributesText" in condition:
                condition_operator = self.__extract_value_from_attribute_text(
                    condition["ExtendedAttributesText"],
                    preceded_by="mdde_JoinOperator,",
                )
                parent_literal = self.__extract_value_from_attribute_text(
                    condition["ExtendedAttributesText"],
                    preceded_by="mdde_ParentLiteralValue,",
                )
            condition["Operator"] = condition_operator
            condition["ParentLiteral"] = parent_literal

            # Condition components (i.e. left and right side of the condition operator)
            lst_components = condition["c:ExtendedCollections"]["o:ExtendedCollection"]
            if isinstance(lst_components, dict):
                lst_components = [lst_components]
            condition["JoinConditionComponents"] = self.__join_condition_components(
                lst_components=lst_components, dict_attributes=dict_attributes
            )
            condition.pop("c:ExtendedCollections")
            lst_conditions[i] = condition

        composition["JoinConditions"] = lst_conditions
        composition.pop("c:ExtendedCompositions")
        return composition

    def __join_condition_components(
        self, lst_components: list, dict_attributes: dict
    ) -> dict:
        """Reroutes, cleans and enriches component data for one join condition

        Args:
            lst_components (list): Join condition component
            dict_attributes (dict): All attributes (in- and external)

        Returns:
            dict: Cleaned, rerouted and enriched join condition component data
        """
        dict_components = {}
        lst_components = self.clean_keys(lst_components)
        for component in lst_components:
            type_component = component["Name"]
            if type_component == "mdde_ChildAttribute":
                # Child attribute
                # TODO: implement alias to child entity
                logger.debug("Added child attribute")
                type_entity = type_entity = [
                    value
                    for value in ["o:Entity", "o:Shortcut", "o:EntityAttribute"]
                    if value in component["c:Content"]
                ][0]
                id_attr = component["c:Content"][type_entity]["@Ref"]
                dict_components["AttributeChild"] = dict_attributes[id_attr]
            elif type_component == "mdde_ParentSourceObject":
                # Alias to point to a composition entity
                logger.debug("Added parent entity alias")
                dict_components["ParentAlias"] = component["c:Content"][
                    "o:ExtendedSubObject"
                ]["@Ref"]
            elif type_component == "mdde_ParentAttribute":
                # Parent attribute
                logger.debug("Added parent attribute")
                type_entity = [
                    value
                    for value in ["o:Entity", "o:Shortcut", "o:EntityAttribute"]
                    if value in component["c:Content"]
                ][0]
                id_attr = component["c:Content"][type_entity]["@Ref"]
                dict_components["AttributeParent"] = dict_attributes[id_attr]
            else:
                logger.warning(
                    f"Unhandled kind of join item in condition '{type_component}'"
                )
        return dict_components

    def __composition_apply_conditions(
        self, composition: dict, dict_attributes: dict
    ) -> dict:
        # TODO: Find what an APPLY composition is
        condition = composition["c:ExtendedCompositions"]["o:ExtendedComposition"]
        composition["JoinConditions"] = self.clean_keys(condition)
        return composition

    def __extract_value_from_attribute_text(
        self, extended_attrs_text: str, preceded_by: str
    ) -> str:
        """Extracts the value which follows a text string, where the value ends and the next \n or at the end of the string

        Args:
            extended_attrs_text (str): The text that contains the value being searched for
            preceded_by (str): The text that should precede the value being searched for

        Returns:
            str: The value associated with the preceding text
        """
        idx_start = extended_attrs_text.find(preceded_by) + len(preceded_by)
        idx_end = extended_attrs_text.find("\n", idx_start)
        idx_end = idx_end if idx_end > -1 else len(extended_attrs_text) + 1
        value = extended_attrs_text[idx_start:idx_end]
        idx_start = value.find("=") + 1
        value = value[idx_start:].upper()
        return value

    # TODO: Remove function
    def __serialize_datetime(self, obj):
        """Retrieves a datetime and formats it to ISO-format

        Args:
            obj (any): Object to be formatted into the correct ISO date format if possible

        Returns:
            Datetime: Formatted in ISO-format
        """

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")
