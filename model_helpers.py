import logging

import logging_config
from model_object import ModelObject

logger = logging.getLogger(__name__)


class Domain(ModelObject):
    """Datatypes to be applied to attributes"""

    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.datatype = dict_pd["a:DataType"]
        if "a:Length" in dict_pd:
            self.length = dict_pd["a:Length"]
        else:
            self.length = None
        if "a:Precision" in dict_pd:
            self.precision = dict_pd["a:Precision"]
        else:
            self.precision = None


class Schema(ModelObject):
    def __init__(self, dict_pd):
        super().__init__(dict_pd)


class DataSourceModel(ModelObject):
    # TODO: Research role
    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        lst_dict_shortcuts = dict_pd["c:BaseDataSource.SourceModels"]
        self.lst_id_shortcut = []
        if "o:Shortcut" in lst_dict_shortcuts:
            lst_shortcuts = lst_dict_shortcuts["o:Shortcut"]
            if isinstance(lst_shortcuts, dict):
                lst_shortcuts = [lst_shortcuts]
            self.lst_id_shortcut = [sub["@Ref"] for sub in lst_shortcuts]


class SourceModel(ModelObject):
    """All models (Schema's)"""

    # TODO: Research role
    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        self.stereotype_target = dict_pd[" a:TargetStereotype"]
        self.id_target = dict_pd["a:TargetID"]
        self.id_class_target = dict_pd["a:TargetClassID"]
