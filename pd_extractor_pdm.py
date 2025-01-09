import logging

import logging_config
from pd_transform_pdm import TransformModels, TransformProcedures, TransformViews


logger = logging.getLogger(__name__)


class PDMObjectExtractor:
    """Collection of functions used to extract the relevant objects from a Power Designer logical data model document"""

    def __init__(self, pd_content):
        self.content = pd_content
        self.transform_model = TransformModels()
        self.transform_procedures = TransformProcedures()
        self.transform_views = TransformViews()
        self.dict_domains = self.__domains()

    def model(self, content: dict) -> dict:
        """_summary_

        Args:
            content (dict): _description_

        Returns:
            dict: _description_
        """
        pass