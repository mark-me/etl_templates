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
        self.timestamp_fields = ["a:CreationDate", "a:ModificationDate"]

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
        for field in self.timestamp_fields:
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
            if "c:Domain" in attr:
                # Reroute domain data
                id_domain = attr["c:Domain"]["o:Domain"]["@Ref"]
                attr["DomainID"] = id_domain

                # Add matching domain data
                keys_domain = {"Name", "Code", "DataType", "Lenght", "Precision"}
                attr_domain = dict_domains[id_domain]
                attr_domain = {
                    k: attr_domain[k] for k in keys_domain if k in attr_domain
                }
                attr.update(attr_domain)
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

    def entities_external(self, lst_entities: list) -> list:
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            entity = lst_entities[i]
            if "c:SubShortcuts" in entity:
                lst_attributes = entity["c:SubShortcuts"]["o:Shortcut"]
                lst_attributes = self.clean_keys(lst_attributes)
                entity["Attributes"] = lst_attributes
                entity.pop("c:SubShortcuts")
            lst_entities[i] = entity
        return lst_entities

    def mappings(
        self, lst_mappings: list, dict_entities: list, dict_attributes: list
    ) -> list:
        lst_mappings = self.clean_keys(lst_mappings)
        for i in range(len(lst_mappings)):
            mapping = lst_mappings[i]
            logger.debug(f"Starting mapping transform for '{mapping['Name']}'")

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

            lst_mappings[i] = mapping
        return lst_mappings

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
        lst_compositions = mapping["c:ExtendedCompositions"]["o:ExtendedComposition"][
            "c:ExtendedComposition.Content"
        ]["o:ExtendedSubObject"]
        lst_compositions = self.clean_keys(lst_compositions)
        for i in range(len(lst_compositions)):
            # Determine composition clause (FROM/JOIN)
            composition = lst_compositions[i]
            composition["CompositionType"] = self.__extract_value_from_attribute_text(
                composition["ExtendedAttributesText"], str_proceeder="mdde_JoinType,"
            )
            # Determine entities involved
            composition = self.__composition_entity(
                composition=composition, dict_entities=dict_entities
            )
            # Join conditions (ON clause)
            if "c:ExtendedCompositions" in composition:
                composition = self.__composition_join_conditions(
                    composition=composition, dict_attributes=dict_attributes
                )
            lst_compositions[i] = composition
        mapping["CompositionObject"] = lst_compositions
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
        composition["EntityAlias"] = entity["Id"]
        composition.pop("c:ExtendedCollections")
        return composition

    def __composition_join_conditions(
        self, composition: dict, dict_attributes: dict
    ) -> dict:
        logger.debug(
            f"Starting join conditions transform for composition '{composition['Name']}'"
        )
        content_conditions = composition["c:ExtendedCompositions"][
            "o:ExtendedComposition"
        ]["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]

        # For one or multiple conditions
        lst_conditions = []
        if "c:ExtendedCollections" in content_conditions:
            lst_conditions = [
                content_conditions["c:ExtendedCollections"]["o:ExtendedCollection"]
            ]
        else:
            for condition in content_conditions:
                condition_new = condition["c:ExtendedCollections"][
                    "o:ExtendedCollection"
                ]
                if "a:ExtendedAttributesText" in condition:
                    condition_new["ExtendedAttributesText"] = condition[
                        "a:ExtendedAttributesText"
                    ]
                lst_conditions.append(condition_new)

        # Restructure each of the conditions
        for i in range(len(lst_conditions)):
            lst_conditions[i] = self.__join_condition_components(
                lst_conditions[i], dict_attributes=dict_attributes
            )

        composition["JoinConditions"] = lst_conditions
        composition.pop("c:ExtendedCompositions")
        return composition

    def __join_condition_components(self, condition: list, dict_attributes: dict):
        if isinstance(condition, dict):
            condition = [condition]

        if len(condition) == 1:
            #"{1626A879-DBAC-4E54-8A36-28FCB761FF3A},MDDE_LDM,130={2AA569D6-094E-4EA8-BBFF-713196E44D4E},mdde_JoinOperator,1=>\n{E9D50277-1E36-464C-9842-5008646943AB},mdde_ParentLiteralValue,1=0"
            Somethi
        else:
            for j in range(len(lst_conditions)):
                condition = lst_conditions[j]
                lst_conditions = self.clean_keys(condition)
                condition_operator = "="
                if "ExtendedAttributesText" in condition:
                    condition_operator = self.__extract_value_from_attribute_text(
                        condition["ExtendedAttributesText"], preceded_by="mdde_JoinOperator,"
                    )
                condition["Operator"] = condition_operator
                type_join_item = condition["Name"]
                if type_join_item == "mdde_ChildAttribute":
                    # Child attribute
                    # TODO: implement alias to child entity
                    id_attr = condition["c:Content"]["o:EntityAttribute"]["@Ref"]
                    condition["AttributeChild"] = dict_attributes[id_attr]
                    condition.pop("c:Content")
                elif type_join_item == "mdde_ParentSourceObject":
                    # Alias to point to a composition entity
                    condition["ParentAlias"] = condition["c:Content"][
                        "o:ExtendedSubObject"
                    ]["@Ref"]
                    condition.pop("c:Content")
                elif type_join_item == "mdde_ParentAttribute":
                    # Parent attribute
                    type_entity = [
                        value
                        for value in ["o:Entity", "o:Shortcut"]
                        if value in condition["c:Content"]
                    ][0]
                    id_attr = condition["c:Content"][type_entity]["@Ref"]
                    condition["AttributeParent"] = dict_attributes[id_attr]
                    condition.pop("c:Content")
                else:
                    logger.warning(
                        f"Unhandled kind of join item in condition '{type_join_item}'"
                    )
                    # TODO: Handling intermediate entities (Business Rules)
                lst_conditions[j] = condition

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
