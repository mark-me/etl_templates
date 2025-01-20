import datetime
import json
import os
from pathlib import Path

import xmltodict
from jinja2 import Environment, FileSystemLoader

from pd_transform_model_internal import TransformModelInternal
from pd_transform_models_external import TransformModelsExternal
from pd_transform_mappings import TransformMappings
from pd_transform_model_physical import TransformModelPhysical

from logging_config import logging
#from pd_extractor_pdm import PDMObjectExtractor

logger = logging.getLogger(__name__)

class PDDocuments:
    """Represents Power Designer model files"""

    def __init__(self, folder_pd: str):
        """Extracts data from a JSON-ed version of a Power Designer document and turns it into an object representation

        Args:
            folder_pd (str): JSON version of a Power Designer document (.pdm)
        """
        lst_files = []
        importfiles = Path(folder_pd)
        importfiles.iterdir()
        importfiles.glob("*.*dm")       
        lst_files = list(importfiles.glob("*.*dm"))
        for file_pd in lst_files:
            PDDocument(file_pd)
        print("")

class PDDocument:
    """Represents Power Designer logical data model file"""

    def __init__(self, file_pd: str):
        """Extracts data from (Logical) Model Power Designer document and turns it into an object representation

        Args:
            file_pd (str): Power Designer data model document (.*dm)
        """
        self.file_pd = file_pd
        # Extracting data from the file
        self.content = self.read_file_model(file_pd=file_pd)
        logger.debug(f"Start model extraction voor bestand '{file_pd}'.") 
        extractor = ObjectExtractor(pd_content=self.content)       
        self.lst_models = extractor.models()
        self.lst_mappings = []
        
    def read_file_model(self, file_pd: str) -> dict:
        """Reading the XML Power Designer ldm file into a dictionary

        Args:
            file_xml (str): The path to a XML file

        Returns:
            dict: The Power Designer data converted to a dictionary
        """
        # Function not yet used, but candidate for reading XML file
        model_extension = Path(file_pd).suffix
        with open(file_pd) as fd:
            doc = fd.read()
        dict_data = xmltodict.parse(doc)
        dict_data["Model"]["o:RootObject"]["c:Children"]["o:Model"]["a:ModelExtension"] = model_extension
        dict_data = dict_data["Model"]["o:RootObject"]["c:Children"]["o:Model"]
        
        return dict_data
    
    def __serialize_datetime(self, obj):
        """Retrieves a datetime and formats it to ISO-format

        Args:
            obj (any): Object to be formatted into the correct ISO date format if possible

        Returns:
            Datetime: Formatted in ISO-format
        """

        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError("Type not serializable")

class ObjectExtractor:
    """Collection of functions used to extract the relevant objects from a Power Designer logical data model document"""

    def __init__(self, pd_content):
        self.content = pd_content
        extenstion = self.content["a:ModelExtension"] 
        if extenstion == ".pdm":
            self.transform_model_physical = TransformModelPhysical()
            self.dict_domains = self.__domains()
        elif extenstion == ".ldm":
            self.transform_model_internal = TransformModelInternal()
            self.transform_models_external = TransformModelsExternal()
            self.transform_mappings = TransformMappings()
            self.dict_domains = self.__domains()
        else:
             logger.error(f"No extractor for extention: '{extenstion}'")  

    def models(self) -> list:
        """Retrieves all models and their corresponding objects used in the PowerDesigner document

        Returns:
            list: List of internal model and external models
        """
        dict_model_internal = {}
        lst_models_external = []
        dict_model_physical = {}
        extenstion = self.content["a:ModelExtension"] 
        if extenstion == ".pdm":
            dict_model_physical = self.__models_physical()
        elif extenstion == ".ldm":
            dict_model_internal = self.__model_internal()
            lst_models_external = self.__models_external()
        else:
             logger.error(f"No model for extention: '{extenstion}'")  
        # Combine models
        lst_models = lst_models_external + [dict_model_internal] + [dict_model_physical]
        return lst_models
    
    def __model_internal(self) -> dict:
        """Retrieves the data on the model which is maintained in the loaded Power Designer document

        Returns:
            dict: All the model's data
        """
        model = self.transform_model_internal.model(content=self.content)
        # Model add entity data
        lst_entity = self.__entities_internal()
        if isinstance(lst_entity, dict):
            lst_entity = [lst_entity]
        model["Entities"] = lst_entity
        model["Relationships"] = self.__relationships(lst_entity=lst_entity)
        return model
    
    def __models_physical(self) -> dict:
        """Retrieves the data on the model which is maintained in the loaded Power Designer document

        Returns:
            dict: All the model's data
        """
        model = self.transform_model_physical.model(content=self.content)
        # Model add table data
        model["Tables"] = self.__tables()
        model["Views"] = self.__views()
        model["Procedures"] = self.__procs()
        return model
    
    def __models_external(self) -> list:
        """Retrieve data on models that are maintained outside of the loaded
        Power Designer document and are used for horizontal lineage

        Returns:
            list: List of external models with all their corresponding elements
        """
        # The models will be derived by looking up the TargetModels associated with the entity shortcuts
        # External entity (shortcut) data
        dict_entities = self.__entities_external()
        # Retain 'TargetModels' have references to entities
        lst_target_model = self.content["c:TargetModels"]["o:TargetModel"]
        lst_models = self.transform_models_external.models(
            lst_models=lst_target_model, dict_entities=dict_entities
        )
        return lst_models
    
    def __entities_internal(self) -> list:
        """Returns all entities of the Power Designer document's model with their attributes and identifiers

        Returns:
            list: Entities
        """
        lst_entity = self.content["c:Entities"]["o:Entity"]
        self.transform_model_internal.entities(lst_entity, dict_domains=self.dict_domains)
        return lst_entity
    
    def __entities_external(self) -> dict:
        """Retrieve the Entities of the external model and their associated entities

        Returns:
            dict: A dict of Entities, where each key contains data on an Entity and their attributes as a value
        """
        # External model entity data
        dict_result = {}
        lst_entities = self.content["c:Entities"]["o:Shortcut"]
        if isinstance(lst_entities, dict):
            lst_entities = [lst_entities]
        lst_entities = self.transform_models_external.entities(lst_entities=lst_entities)
        for entity in lst_entities:
            #logger.debug(f"Found external entity shortcut for '{entity["Name"]}'")
            dict_result[entity["Id"]] = entity
        return dict_result
    
    def __tables(self) -> dict:
        """Retrieve the Tables of the model

        Returns:
            dict: A dict of Tables, where each key contains data on an Table and their columns as a value
        """
        # Model table data
        lst_table = self.content["c:Tables"]["o:Table"]
        self.transform_model_physical.tables(lst_table, dict_domains=self.dict_domains)
        return lst_table

    def __domains(self) -> dict:
        dict_domains = {}
        if "c:Domains" in self.content:
            extenstion = self.content["a:ModelExtension"] 
            if extenstion == ".pdm":
                lst_domains = self.content["c:Domains"]["o:PhysicalDomain"]
                dict_domains = self.transform_model_physical.domains(lst_domains=lst_domains)
            elif extenstion == ".ldm":
                lst_domains = self.content["c:Domains"]["o:Domain"]
                dict_domains = self.transform_model_internal.domains(lst_domains=lst_domains)
        else:
            modelname = self.content["a:Name"]
            logger.error(f"In het model '{modelname}' zijn geen domains opgenomen.")
        return dict_domains

    def __relationships(self, lst_entity: list) -> list:
        lst_relationships = []
        if "c:Relationships" in self.content:
            lst_pd_relationships = self.content["c:Relationships"]["o:Relationship"]
            lst_relationships = self.transform_model_internal.relationships(
                lst_relationships=lst_pd_relationships, lst_entity=lst_entity
            )
        return lst_relationships
    
    def __views(self) -> list:
        """Retrieve the Views of the model

        Returns:
            dict: A dict of Views
        """
        lst_views = []
        # Model view data
        if "c:Views" in self.content:
            lst_view = self.content["c:Views"]["o:View"]
            lst_views = self.transform_model_physical.view(lst_view)
        else:
            modelname = self.content["Name"]
            logger.warning(f"In het model '{modelname}' zijn geen views opgenomen.")
        #return lst_view
        
        return lst_views

    def __procs(self) -> list:
        """Retrieve the Procedures of the model

        Returns:
            dict: A dict of Procedures
        """
        lst_procs = []
        if "c:Procedures" in self.content:
            lst_proc = self.content["c:Procedures"]["o:Procedure"]
            lst_procs = self.transform_model_physical.procs(lst_proc)
        else:
            modelname = self.content["Name"]
            logger.warning(f"In het model '{modelname}' zijn geen Procedures opgenomen.")
        return lst_procs

    def mappings(self, dict_entities: list, dict_attributes: list) -> list:
        lst_mappings = self.content["c:Mappings"]["o:DefaultObjectMapping"]
        lst_mappings = self.transform_mappings.mappings(
            lst_mappings=lst_mappings,
            dict_entities=dict_entities,
            dict_attributes=dict_attributes,
        )
        return lst_mappings

# Run Current Class
if __name__ == "__main__":
    folder_models = "input/"  # "input"
    PDDocuments(folder_pd=folder_models)
    print("Done")
