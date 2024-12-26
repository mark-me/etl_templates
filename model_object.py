
import logging

import logging_config

logger = logging.getLogger(__name__)


class ModelObject:
    """Abstract class to fill all common denominators from PowerDesigner
    * id = Identifier
    * name = Name
    * code = Name?
    """

    def __init__(self, dict_pd: dict):
        self.id = dict_pd["@Id"]
        self.name = dict_pd["a:Name"]
        logger.debug(f"Created object {type(self).__name__}: {self.name}")
        if "a:Code" in dict_pd:
            self.code = dict_pd["a:Code"]
        else:
            self.code = None

    def as_dict(self) -> dict:
        return self.__dict__