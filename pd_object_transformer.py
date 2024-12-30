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
            # Reroute attributes
            lst_attrs = lst_entities[i]["c:Attributes"]["o:EntityAttribute"]
            if isinstance(lst_attrs, dict):
                lst_attrs = [lst_attrs]
            lst_attrs = self.attributes_internal(
                lst_attrs=lst_attrs, dict_domains=dict_domains
            )
            lst_entities[i]["Attributes"] = lst_attrs
            lst_entities[i].pop("c:Attributes")
            # Create subset of attributes to enrich identifier attributes
            dict_attrs = {
                attr["Id"]: {"Name": attr["Name"], "Code": attr["Code"]}
                for attr in lst_attrs
            }

            # Set primary identifiers as an attribute of the identifiers
            has_primary = "c:PrimaryIdentifier" in lst_entities[i]
            if has_primary:
                primary_id = lst_entities[i]["c:PrimaryIdentifier"]["o:Identifier"][
                    "@Ref"
                ]

            # Reroute indentifiers
            if "c:Identifiers" in lst_entities[i]:
                identifiers = lst_entities[i]["c:Identifiers"]["o:Identifier"]
                if isinstance(identifiers, dict):
                    identifiers = [identifiers]
                identifiers = self.clean_keys(identifiers)
                # Clean and transform indentifier data
                for j in range(len(identifiers)):
                    lst_attr_id = identifiers[j]["c:Identifier.Attributes"][
                        "o:EntityAttribute"
                    ]
                    if isinstance(lst_attr_id, dict):
                        lst_attr_id = [lst_attr_id]
                    lst_attr_id = [dict_attrs[d["@Ref"]] for d in lst_attr_id]
                    identifiers[j]["Attributes"] = lst_attr_id
                    identifiers[j].pop("c:Identifier.Attributes")
                    # Set primary identifier attribute
                    if has_primary:
                        identifiers[j]["IsPrimary"] = primary_id == identifiers[j]["Id"]
                lst_entities[i]["Identifiers"] = identifiers
                lst_entities[i].pop("c:Identifiers")
                lst_entities[i].pop("c:PrimaryIdentifier")
                lst_entities[i] = self.clean_keys(lst_entities[i])
                # Reroute default mapping
                # TODO: research role DefaultMapping
        return lst_entities

    def attributes_internal(self, lst_attrs: list, dict_domains: list) -> list:
        lst_attrs = self.clean_keys(lst_attrs)
        for i in range(len(lst_attrs)):
            # Change domain data
            if "c:Domain" in lst_attrs[i]:
                # Reroute domain data
                id_domain = lst_attrs[i]["c:Domain"]["o:Domain"]["@Ref"]
                lst_attrs[i]["DomainID"] = id_domain

                # Add matching domain data
                keys_domain = {"Name", "Code", "DataType", "Lenght", "Precision"}
                attr_domain = dict_domains[id_domain]
                attr_domain = {
                    k: attr_domain[k] for k in keys_domain if k in attr_domain
                }
                lst_attrs[i].update(attr_domain)
                lst_attrs[i].pop("c:Domain")
        return lst_attrs

    def entities_external(self, lst_entities: list) -> list:
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            if "c:SubShortcuts" in lst_entities[i]:
                lst_attributes = lst_entities[i]["c:SubShortcuts"]["o:Shortcut"]
                lst_attributes = self.clean_keys(lst_attributes)
                lst_entities[i]["Attributes"] = lst_attributes
                lst_entities[i].pop("c:SubShortcuts")
        return lst_entities

    def mappings(
        self, lst_mappings: list, dict_entities: list, dict_attributes: list
    ) -> list:
        lst_mappings = self.clean_keys(lst_mappings)
        i = 0
        for i in range(len(lst_mappings)):
            logger.debug(f"Starting mapping transform for '{lst_mappings[i]['Name']}'")
            # Target entity rerouting and enriching
            id_entity_target = lst_mappings[i]["c:Classifier"]["o:Entity"]["@Ref"]
            lst_mappings[i]["EntityTarget"] = dict_entities[id_entity_target]
            lst_mappings[i].pop("c:Classifier")
            # Source entities rerouting and enriching
            lst_source_entity = []
            for entity_type in ["o:Entity", "o:Shortcut"]:
                if entity_type in lst_mappings[i]["c:SourceClassifiers"]:
                    source_entity = lst_mappings[i]["c:SourceClassifiers"][entity_type]
                    if isinstance(source_entity, dict):
                        source_entity = [source_entity]
                    source_entity = [d["@Ref"] for d in source_entity]
                    lst_source_entity = lst_source_entity + source_entity
            lst_source_entity = [dict_entities[item] for item in lst_source_entity]
            lst_mappings[i]["EntitiesSource"] = lst_source_entity
            lst_mappings[i].pop("c:SourceClassifiers")
            # Reroute datasource
            # TODO: Research role of DataSource
            lst_mappings[i]["DataSourceID"] = lst_mappings[i]["c:DataSource"][
                "o:DefaultDataSource"
            ]["@Ref"]
            lst_mappings[i].pop("c:DataSource")

            # Rerouting compositionObjects
            lst_compositions = lst_mappings[i]["c:ExtendedCompositions"][
                "o:ExtendedComposition"
            ]["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
            lst_compositions = self.__mapping_compositions(
                lst_compositions=lst_compositions,
                dict_entities=dict_entities,
                dict_attributes=dict_attributes,
            )

            lst_mappings[i]["CompositionObject"] = lst_compositions
            lst_mappings[i].pop("c:ExtendedCompositions")

        return lst_mappings

    def __mapping_compositions(
        self, lst_compositions: list, dict_entities: dict, dict_attributes: dict
    ) -> list:
        lst_compositions = self.clean_keys(lst_compositions)
        for i in range(len(lst_compositions)):
            # Determine composition clause (FROM/JOIN)
            lst_compositions[i]["CompositionType"] = self.__mapping_extract_join_type(
                lst_compositions[i]["ExtendedAttributesText"]
            )
            # Determine entity involved
            collection = lst_compositions[i]["c:ExtendedCollections"][
                "o:ExtendedCollection"
            ]
            collection = self.__composition_entities(dict_entities, collection)
            lst_compositions[i]["Entities"] = collection
            lst_compositions[i].pop("c:ExtendedCollections")

            test_composition = lst_compositions[i]
            # Join items (ON clause)
            # TODO : Figure this shit out... Where is the join operator?
            if "c:ExtendedCompositions" in lst_compositions[i]:
                test = lst_compositions[i]["c:ExtendedCompositions"][
                    "o:ExtendedComposition"
                ]["c:ExtendedComposition.Content"]["o:ExtendedSubObject"]
                lst_join_items = lst_compositions[i]["c:ExtendedCompositions"][
                    "o:ExtendedComposition"
                ]["c:ExtendedComposition.Content"]["o:ExtendedSubObject"][
                    "c:ExtendedCollections"
                ]["o:ExtendedCollection"]
                lst_compositions[2]["c:ExtendedCompositions"]["o:ExtendedComposition"][
                    "c:ExtendedComposition.Content"
                ]["o:ExtendedSubObject"]
                lst_join_items = self.__composition_join_items(
                    lst_join_items=lst_join_items, dict_attributes=dict_attributes
                )
                lst_compositions[i]["JoinAttributes"] = lst_join_items
                lst_compositions[i].pop("c:ExtendedCompositions")

        return lst_compositions

    def __composition_entities(self, collection: dict, dict_entities: dict) -> dict:
        collection = self.clean_keys(collection)
        if "c:Content" in collection:
            type_entity = [
                value
                for value in ["o:Entity", "o:Shortcut"]
                if value in collection["c:Content"]
            ][0]
            id_entity = collection["c:Content"][type_entity]["@Ref"]
            collection["Entity"] = dict_entities[id_entity]
            collection.pop("c:Content")
        return collection

    def __composition_join_items(
        self, lst_join_items: list, dict_attributes: dict
    ) -> list:
        lst_join_items = self.clean_keys(lst_join_items)
        for j in range(len(lst_join_items)):
            type_join_item = lst_join_items[j]["Name"]
            if type_join_item == "mdde_ChildAttribute":
                print("Child attribute")
                id_attr = lst_join_items[j]["c:Content"]["o:EntityAttribute"]["@Ref"]
                lst_join_items[j]["AttributeChild"] = dict_attributes[id_attr]
                lst_join_items[j].pop("c:Content")
            elif type_join_item == "mdde_ParentSourceObject":
                # TODO: Link to from composition
                print("Link to FROM")
            elif type_join_item == "mdde_ParentAttribute":
                type_entity = [
                    value
                    for value in ["o:Entity", "o:Shortcut"]
                    if value in lst_join_items[j]["c:Content"]
                ][0]
                id_attr = lst_join_items[j]["c:Content"][type_entity]["@Ref"]
                lst_join_items[j]["AttributeParent"] = dict_attributes[id_attr]
                lst_join_items[j].pop("c:Content")
            else:
                logger.warning(f"Unhandled kind of join '{type_join_item}'")
        return lst_join_items

    def __mapping_extract_join_type(self, extended_attrs_text: str) -> str:
        """Extracting the FROM or JOIN type clause from a very specific Power Designer attributes

        Args:
            extended_attrs_text (str): ExtendedAttributesText

        Returns:
            str: FROM or JOIN type
        """
        str_proceeder = "mdde_JoinType,"
        idx_start = extended_attrs_text.find(str_proceeder) + len(str_proceeder)
        idx_end = extended_attrs_text.find("\n", idx_start)
        idx_end = idx_end if idx_end > -1 else len(extended_attrs_text) + 1
        join_type = extended_attrs_text[idx_start:idx_end]
        idx_start = join_type.find("=") + 1
        join_type = join_type[idx_start:].upper()
        return join_type
