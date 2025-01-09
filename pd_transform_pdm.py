import logging

import logging_config
from pd_transform_object import ObjectTransformer

logger = logging.getLogger(__name__)


class TransformModels(ObjectTransformer):
    def __init__(self):
        super().__init__()

class TransformProcedures(ObjectTransformer):
    def __init__(self):
        super().__init__()

class TransformViews(ObjectTransformer):
    def __init__(self):
        super().__init__()
