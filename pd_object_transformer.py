from datetime import datetime
import logging
from typing import Union

import logging_config

logger = logging.getLogger(__name__)


class ObjectTransformer:
    """Collection of functions that transform structures and data on Power Designer objects.

    Transforming structures is done to simplify 'querying' the data for ETL and DDL
    """

    def __init__(self):
        self.__timestamp_fields = ["a:CreationDate", "a:ModificationDate"]

    def clean_keys(self, content: Union[dict, list]):
        """Renames keys of Power Designer objects (i.e. dictionaries) so the '@' and 'a:' prefixes are removed

        Args:
            content (Union[dict, list]): A dict or list of dicts with Power Designer objects

        Returns:
            _type_: List or dict with renamed keys (depending on what type was passed as a parameter)
        """
        if isinstance(content, dict):
            lst_object = [content]
        else:
            lst_object = content
        for i in range(len(lst_object)):
            attrs = [key for key in list(lst_object[i].keys()) if key[:1] == "@"]
            for attr in attrs:
                lst_object[i][attr[1:]] = lst_object[i].pop(attr)
            attrs = [key for key in list(lst_object[i].keys()) if key[:2] == "a:"]
            for attr in attrs:
                lst_object[i][attr[2:]] = lst_object[i].pop(attr)

        if isinstance(content, dict):
            result = lst_object[0]
        else:
            result = lst_object
        return result

    def convert_values_datetime(self, d: dict, convert_key: str) -> dict:
        """Converts all (nested) dictionary entries with a specified name value containing a Unix timestamp to a datetime object

        Args:
            d (dict): Dictionary contains the timestamp value
            remove_key (str): The name of the keys that contains the timestamp value

        Returns:
            dict: The dictionary without the keys
        """
        if isinstance(d, dict):
            for key in list(d.keys()):
                if key == convert_key:
                    d[key] = datetime.fromtimestamp(int(d[key]))
                else:
                    self.convert_values_datetime(d[key], convert_key)
            return d
        elif isinstance(d, list):
            for i in range(len(d)):
                d[i] = self.convert_values_datetime(d[i], convert_key)
            return d

    def convert_timestamps(self, pd_content: dict) -> dict:
        for field in self.__timestamp_fields:
            pd_content = self.convert_values_datetime(pd_content, field)
        return pd_content

    def entities_internal(self, lst_entities: list, dict_domains: dict) -> list:
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            entity = lst_entities[i]

            # Reroute attributes
            entity = self.__entity_internal_attributes(
                entity=entity, dict_domains=dict_domains
            )
            # Create subset of attributes to enrich identifier attributes
            dict_attrs = {
                d["Id"]: {"Name": d["Name"], "Code": d["Code"]}
                for d in entity["Attributes"]
            }

            # Identifiers and primary identifier
            entity = self.__entity_internal_identifiers(
                entity=entity, dict_attrs=dict_attrs
            )

            # Reroute default mapping
            # TODO: research role DefaultMapping
            lst_entities[i] = entity
        return lst_entities

    def __entity_internal_attributes(self, entity: dict, dict_domains: list) -> dict:
        lst_attrs = entity["c:Attributes"]["o:EntityAttribute"]
        if isinstance(lst_attrs, dict):
            lst_attrs = [lst_attrs]
        lst_attrs = self.clean_keys(lst_attrs)
        for i in range(len(lst_attrs)):
            # Change domain data
            attr = lst_attrs[i]
            attr["Order"] = i
            if "c:Domain" in attr:
                # Reroute domain data
                id_domain = attr["c:Domain"]["o:Domain"]["@Ref"]

                # Add matching domain data
                attr_domain = dict_domains[id_domain]
                keys_domain = {"Id", "Name", "Code", "DataType", "Lenght", "Precision"}
                attr_domain = {
                    k: attr_domain[k] for k in keys_domain if k in attr_domain
                }
                attr["Domain"] = attr_domain
                attr.pop("c:Domain")
            lst_attrs[i] = attr
        entity["Attributes"] = lst_attrs
        entity.pop("c:Attributes")
        return entity

    def __entity_internal_identifiers(self, entity: dict, dict_attrs: dict) -> dict:
        # Set primary identifiers as an attribute of the identifiers
        has_primary = "c:PrimaryIdentifier" in entity
        if has_primary:
            primary_id = entity["c:PrimaryIdentifier"]["o:Identifier"]["@Ref"]

        # Reroute indentifiers
        if "c:Identifiers" in entity:
            identifiers = entity["c:Identifiers"]["o:Identifier"]
            if isinstance(identifiers, dict):
                identifiers = [identifiers]
            identifiers = self.clean_keys(identifiers)
            # Clean and transform indentifier data
            for j in range(len(identifiers)):
                identifier = identifiers[j]
                identifier["EntityID"] = entity["Id"]
                identifier["EntityName"] = entity["Name"]
                identifier["EntityCode"] = entity["Code"]
                if "c:Identifier.Attributes" not in identifier:
                    logger.error(
                        f"No attributes included in the identifier '{identifier["Name"]}'"
                    )
                else:
                    lst_attr_id = identifier["c:Identifier.Attributes"][
                        "o:EntityAttribute"
                    ]
                    if isinstance(lst_attr_id, dict):
                        lst_attr_id = [lst_attr_id]
                    lst_attr_id = [dict_attrs[d["@Ref"]] for d in lst_attr_id]
                    identifier["Attributes"] = lst_attr_id
                    identifier.pop("c:Identifier.Attributes")
                # Set primary identifier attribute
                if has_primary:
                    identifier["IsPrimary"] = primary_id == identifier["Id"]
                identifiers[j] = identifier
            entity["Identifiers"] = identifiers
            entity.pop("c:Identifiers")
            entity.pop("c:PrimaryIdentifier")
        return entity

    def relationships(self, lst_relationships: list, lst_entity: list) -> list:
        """Cleans and enriches relationship data

        Args:
            lst_relationships (list): Power Designer items describing a relationship between entities
            lst_entity (dict): Contains all entities

        Returns:
            list: _description_
        """
        # Creating dictionaries to simplify adding data to relationships
        dict_entities = {entity["Id"]: entity for entity in lst_entity}
        dict_attributes = {
            attr["Id"]: attr for entity in lst_entity for attr in entity["Attributes"]
        }
        dict_identifiers = {
            ids["Id"]: ids
            for entity in lst_entity
            if "Identifiers" in entity
            for ids in entity["Identifiers"]
        }

        # Processing relationships
        lst_relationships = self.clean_keys(lst_relationships)
        if isinstance(lst_relationships, dict):
            lst_relationships = [lst_relationships]
        for i in range(len(lst_relationships)):
            relationship = lst_relationships[i]
            # Add entity data
            self.__relationship_entities(
                relationship=relationship, dict_entities=dict_entities
            )
            # Add attribute data
            relationship = self.__relationship_join(
                relationship=relationship, dict_attributes=dict_attributes
            )
            # Add identifier data
            relationship = self.__relationship_identifiers(
                relationship=relationship, dict_identifiers=dict_identifiers
            )
            lst_relationships[i] = relationship

        return lst_relationships

    def __relationship_entities(self, relationship: dict, dict_entities: dict) -> dict:
        id_entity = relationship["c:Object1"]["o:Entity"]["@Ref"]
        relationship["Entity1"] = dict_entities[id_entity]
        relationship.pop("c:Object1")
        id_entity = relationship["c:Object2"]["o:Entity"]["@Ref"]
        relationship["Entity2"] = dict_entities[id_entity]
        relationship.pop("c:Object2")
        return relationship

    def __relationship_join(self, relationship: dict, dict_attributes: dict) -> dict:
        """Reroute and add entity attribute data to joins

        Args:
            relationship (dict): The relationship containing the join(s)
            dict_attributes (dict): Attributes which is used to enrich the set

        Returns:
            dict: _description_
        """
        lst_joins = relationship["c:Joins"]["o:RelationshipJoin"]
        if isinstance(lst_joins, dict):
            lst_joins = [lst_joins]
        lst_joins = self.clean_keys(lst_joins)
        for i in range(len(lst_joins)):
            join = {}
            join["Order"] = i
            id_attr = lst_joins[i]["c:Object1"]["o:EntityAttribute"]["@Ref"]
            join["Entity1Attribute"] = dict_attributes[id_attr]
            id_attr = lst_joins[i]["c:Object2"]["o:EntityAttribute"]["@Ref"]
            join["Entity2Attribute"] = dict_attributes[id_attr]
            lst_joins[i] = join
        relationship["Joins"] = lst_joins
        relationship.pop("c:Joins")
        return relationship

    def __relationship_identifiers(
        self, relationship: dict, dict_identifiers: dict
    ) -> dict:
        lst_indentifier_id = relationship["c:ParentIdentifier"]["o:Identifier"]
        if isinstance(lst_indentifier_id, dict):
            lst_indentifier_id = [lst_indentifier_id]
        relationship["Indentifiers"] = [
            dict_identifiers[id["@Ref"]] for id in lst_indentifier_id
        ]
        relationship.pop("c:ParentIdentifier")
        return relationship

    def models_external(self, lst_models: list, dict_entities: dict) -> list:
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
        return lst_result

    def entities_external(self, lst_entities: list) -> list:
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            entity = lst_entities[i]
            if "c:FullShortcutReplica" in entity:
                entity.pop("c:FullShortcutReplica")
            self.__entity_external_attribute(entity)
            entity.pop("c:SubShortcuts")
            lst_entities[i] = entity
        return lst_entities

    def __entity_external_attribute(self, entity: dict) -> dict:
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

    def mappings(
        self, lst_mappings: list, dict_entities: dict, dict_attributes: dict
    ) -> list:
        lst_ignored_mapping = [
            "Mapping Br Custom Business Rule Example",
            "Mapping AggrTotalSalesPerCustomer",
            "Mapping Pivot Orders Per Country Per Date",
        ]  # TODO: Ignored mappings for 1st version
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
            id_entity_target = mapping["c:Classifier"]["o:Entity"]["@Ref"]
            mapping["EntityTarget"] = dict_entities[id_entity_target]
            logger.debug(f"Mapping target entity: '{mapping["EntityTarget"]['Name']}'")
            mapping.pop("c:Classifier")

            # Source entities rerouting and enriching
            mapping = self.__mapping_entities_source(
                mapping=mapping, dict_entities=dict_entities
            )
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
                if "c:ExtendedCollections" in attr_map:
                    attr_map["CompositionEntityAlias"] = attr_map[
                        "c:ExtendedCollections"
                    ]["o:ExtendedCollection"]["c:Content"]["o:ExtendedSubObject"][
                        "@Ref"
                    ]
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
                    attr_map.pop("c:SourceFeatures")

                lst_attr_maps[i] = attr_map
            mapping["AttributeMapping"] = lst_attr_maps
            mapping.pop("c:StructuralFeatureMaps")
        return mapping

    def __mapping_entities_source(self, mapping: dict, dict_entities: dict) -> dict:
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
    ) -> list:
        logger.debug(f"Starting compositions transform for mapping '{mapping['Name']}'")
        lst_compositions = mapping["c:ExtendedCompositions"]["o:ExtendedComposition"]
        if "c:ExtendedComposition.Content" in lst_compositions:
            lst_compositions = lst_compositions["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
            logger.error("Composition is different")
        lst_compositions = self.clean_keys(lst_compositions)
        for i in range(len(lst_compositions)):
            composition = lst_compositions[i]
            composition["Order"] = i
            # Determine composition clause (FROM/JOIN)
            composition["CompositionType"] = self.__extract_value_from_attribute_text(
                composition["ExtendedAttributesText"], preceded_by="mdde_JoinType,"
            )
            logger.debug(
                f"Composition {composition["CompositionType"]} for '{composition["Name"]}'"
            )
            # Determine entities involved
            composition = self.__composition_entity(
                composition=composition, dict_entities=dict_entities
            )
            # Join conditions (ON clause)
            if "c:ExtendedCompositions" in composition:
                if composition["CompositionType"] != "APPLY":
                    composition = self.__composition_join_conditions(
                        composition=composition, dict_attributes=dict_attributes
                    )
                else:
                    composition = self.__composition_apply_conditions(
                        composition=composition, dict_attributes=dict_attributes
                    )
            lst_compositions[i] = composition
        mapping["Compositions"] = lst_compositions
        mapping.pop("c:ExtendedCompositions")
        return mapping

    def __composition_entity(self, composition: dict, dict_entities: dict) -> dict:
        logger.debug(
            f"Starting entity transform for composition '{composition['Name']}'"
        )
        entity = composition["c:ExtendedCollections"]["o:ExtendedCollection"]
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
        composition.pop("c:ExtendedCollections")
        return composition

    def __composition_join_conditions(
        self, composition: dict, dict_attributes: dict
    ) -> dict:
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
                f"Join conditions transform for {str(i)}) '{condition["Name"]}'"
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
        condition = composition["c:ExtendedCompositions"]["o:ExtendedComposition"]
        composition["JoinConditions"] = self.clean_keys(condition)
        return composition

    def __extract_value_from_attribute_text(
        self, extended_attrs_text: str, preceded_by: str
    ) -> str:
        idx_start = extended_attrs_text.find(preceded_by) + len(preceded_by)
        idx_end = extended_attrs_text.find("\n", idx_start)
        idx_end = idx_end if idx_end > -1 else len(extended_attrs_text) + 1
        value = extended_attrs_text[idx_start:idx_end]
        idx_start = value.find("=") + 1
        value = value[idx_start:].upper()
        return value
