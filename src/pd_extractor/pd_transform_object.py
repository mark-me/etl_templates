from datetime import datetime
import logging
from typing import Union

import src.log_config.logging_config as logging_config

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

    def __convert_values_datetime(self, d: dict, convert_key: str) -> dict:
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
                    self.__convert_values_datetime(d[key], convert_key)
            return d
        elif isinstance(d, list):
            for i in range(len(d)):
                d[i] = self.__convert_values_datetime(d[i], convert_key)
            return d

    def convert_timestamps(self, pd_content: dict) -> dict:
        """Converts all unix time integers to datetime objects according to the list of fieldnames specified in the constructor

        Args:
            pd_content (dict): Power Designer document data

        Returns:
            dict: The same Power Designer document data, but with timestamps converted
        """
        for field in self.__timestamp_fields:
            pd_content = self.__convert_values_datetime(pd_content, field)
        return pd_content
