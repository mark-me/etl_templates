from datetime import datetime
from typing import Union

import logging

import logging_config


class ObjectTransformer:
    def __init__(self):
        self.timestamp_fields = ["a:CreationDate", "a:ModificationDate"]

    def clean_keys(self, content: Union[dict, list]):
        if isinstance(content, dict):
            lst_object = [content]
        else:
            lst_object = content
        i = 0
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
        """Remove keys from a nested dictionary, also from the dictionaries within lists (Currently not used)

        Args:
            d (dict): Dictionary that needs cleaning
            remove_key (str): The name of the keys that needs to be removed

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
        i = 0
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
                # Clean and transform indentifier data
                for j in range(len(identifiers)):
                    identifiers[j] = self.clean_keys(identifiers[j])
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
                        identifiers[j]["IsPrimary"] = (
                            primary_id == identifiers[j]["Id"]
                        )
                lst_entities[i]["Identifiers"] = identifiers
                lst_entities[i].pop("c:Identifiers")
                lst_entities[i].pop("c:PrimaryIdentifier")

                lst_entities[i] = self.clean_keys(lst_entities[i])
                # Reroute default mapping
                # TODO: research role DefaultMapping
        return lst_entities

    def attributes_internal(self, lst_attrs: list, dict_domains: list) -> list:
        i = 0
        for i in range(len(lst_attrs)):
            lst_attrs[i] = self.clean_keys(lst_attrs[i])

            # Change domain data
            if "c:Domain" in lst_attrs[i]:
                # Reroute domain data
                id_domain = lst_attrs[i]["c:Domain"]["o:Domain"]["@Ref"]
                lst_attrs[i]["DomainID"] = id_domain

                # Add matching domain data
                keys_domain = {'Name', 'Code', 'DataType', 'Lenght', 'Precision'}
                attr_domain = dict_domains[id_domain]
                attr_domain = {k: attr_domain[k] for k in keys_domain if k in attr_domain}
                lst_attrs[i].update(attr_domain)
                lst_attrs[i].pop("c:Domain")
        return lst_attrs

    def entities_external(self, lst_entities: list) -> list:
        i = 0
        for i in range(len(lst_entities)):
            lst_entities[i] = self.clean_keys(lst_entities[i])
            if 'c:SubShortcuts' in lst_entities[i]:
                lst_attributes = lst_entities[i]['c:SubShortcuts']['o:Shortcut']
                lst_attributes = self.clean_keys(lst_attributes)
                lst_entities[i]["Attributes"] = lst_attributes
                lst_entities[i].pop('c:SubShortcuts')
        return lst_entities

#    def attributes_external(self, lst_attrs: list) -> list:

