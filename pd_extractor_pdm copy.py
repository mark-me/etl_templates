import logging

import logging_config
from pd_transform_pdm import TransformModels, TransformProcedures, TransformViews, TransformDomains


logger = logging.getLogger(__name__)


class PDMObjectExtractor:
    """Collection of functions used to extract the relevant objects from a Power Designer logical data model document"""

    def __init__(self, pd_content):
        self.content = pd_content
        self.transform_model = TransformModels()
        self.transform_procedures = TransformProcedures()
        self.transform_views = TransformViews()
        self.dict_domains = self.__domains()

    def models(self) -> list:
        """Retrieves all models and their corresponding objects used in the PowerDesigner document

        Returns:
            list: List of internal model and external models
        """
        lst_models = self.__model()
        return lst_models
    
    def views(self) -> dict:
        """Retrieves all views and their corresponding objects used in the PowerDesigner document

        Returns:
            dict: dict of views
        """
        dict_views= self.__views()
        return dict_views
    
    def procs(self) -> dict:
        """Retrieves all procedures and their corresponding objects used in the PowerDesigner document

        Returns:
            dict: dict of procedure
        """
        dict_procs= self.__procs()
        return dict_procs
    
    def __model(self) -> dict:
        """Retrieves the data on the model which is maintained in the loaded Power Designer document

        Returns:
            dict: All the model's data
        """
        model = self.transform_model.model(content=self.content)
        # Model add table data
        lst_table = self.__tables()
        #if isinstance(lst_entity, dict):
        #    lst_entity = [lst_entity]
        model["Tables"] = lst_table
        #model["Relationships"] = self.__relationships(lst_entity=lst_entity)
        return model
    
    def __tables(self) -> dict:
        """Retrieve the Tables of the model

        Returns:
            dict: A dict of Tables, where each key contains data on an Table and their columns as a value
        """
        # Model table data
        lst_table = self.content["c:Tables"]["o:Table"]
        self.transform_model.tables(lst_table, dict_domains=self.dict_domains)
        return lst_table
    
    def __domains(self) -> dict:
        dict_domains = {}
        lst_domains = self.content["c:Domains"]["o:PhysicalDomain"]
        dict_domains = self.transform_model.domains(lst_domains=lst_domains)
        return dict_domains    
    
    def __views(self) -> dict:
        """Retrieve the Views of the model

        Returns:
            dict: A dict of Views
        """
        # Model view data
        lst_view = self.content["c:Views"]["o:View"]
        #return lst_view
        dict_views = self.transform_views.view(lst_view)
        return dict_views
    
    def __procs(self) -> dict:
        """Retrieve the Procedures of the model

        Returns:
            dict: A dict of Procedures
        """
        lst_procs = self.content["c:Procedures"]["o:Procedure"]
        dict_procs = self.transform_procedures.procs(lst_procs)
        return dict_procs