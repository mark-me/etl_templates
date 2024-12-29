from datetime import datetime

import logging

import logging_config

class ObjectCleaner:
    def __init__(self):
        self.timestamp_fields = ['a:CreationDate', 'a:ModificationDate']

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

    def entity_internal(self, lst_entities: list) -> list:
        i = 0
        for i in range(len(lst_entities)):
            attributes = lst_entities[i]['c:Attributes']['o:EntityAttribute']
            lst_entities[i]["Attributes"] = lst_entities[i]['c:Attributes']['o:EntityAttribute']
            lst_entities[i].pop("c:Attributes")
            if 'c:Identifiers' in lst_entities[i]:
                idenitifiers = lst_entities[i]['c:Identifiers']['o:Identifier']
                if isinstance(idenitifiers, dict):
                    idenitifiers = [idenitifiers]
                lst_entities[i]["Identifiers"] = idenitifiers
                lst_entities[i].pop("c:Identifiers")
        return lst_entities
