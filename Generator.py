import datetime
import json
from pathlib import Path

import xmltodict
from jinja2 import Environment, FileSystemLoader

from logging_config import logging

logger = logging.getLogger(__name__)

"""Reading the XML Power Designer ldm file into a dictionary

        Args:
            file_input (str): The path to a JSON file

        Returns:
            dict: The JSON (Power Designer model data) converted to a dictionary
        """


class Generator:
    def __init__(self, file_input: str):
        self.file_input = file_input
        # Extracting data from the file
        self.content = self.__read_file_model(file_input=file_input)
        self.templates = self.__get_templates()
        self.ddls = self.__generate_ddl()
        
        print("")
    
    def __read_file_model(self, file_input: str) -> dict:
        """Reading the XML Power Designer ldm file into a dictionary

        Args:
            file_input (str): The path to a JSON file

        Returns:
            dict: The JSON (Power Designer model data) converted to a dictionary
        """
        # Function not yet used, but candidate for reading XML file
        with open(file_input) as json_file:
            self.dict_model = json.load(json_file)
        return self.dict_model
    
    def __get_templates(self):
        """
        Creates the DDL's

        Args:
         type_template (str): The type of templates your want to use to implement your models
            dict_object (dect): The object that describes the object for the template
        """
        # Loading templates
        dest_type = "dedicated-pool"
        dir_template = "templates/" + dest_type + "/"
        environment = Environment(
            loader=FileSystemLoader(dir_template), trim_blocks=True, lstrip_blocks=True
        )
        self.dict_templates = {
            "schema": environment.get_template("create_schema.sql"),
            "Tables": environment.get_template("create_table.sql"),
            "Entities": environment.get_template("create_entity.sql"),
            "Views": environment.get_template("create_view.sql"),
            "Procedures": environment.get_template("create_procedure.sql"),
        }
        return self.dict_templates
    
    def __generate_ddl(self):
        print("")
        self.lst_ddls = []
        lst_objects = []
        print("")
        self.dict_templates.items()
        print("")
        for type_object, template in self.dict_templates.items():
            print("")
            for model in self.dict_model["Models"]:
                print(model["IsDocumentModel"])
                if model["IsDocumentModel"]: 
                    if type_object in model:
                        lst_objects = []
                        lst_objects = model[type_object]
                        for i, object in enumerate(lst_objects):
                            object["Schema"] = model["Code"]
                            lst_objects[i] = object
                        #self.lst_ddls.append(
                        #    {"type": type_object, "template": template, "objects": lst_objects})
                    else:
                        logger.warning(f"Object for '{type_object}' does not exist in the model.")
            self.lst_ddls.append(
                {"type": type_object, "template": template, "objects": lst_objects})
        print("")
        return self.lst_ddls

# Run Current Class
if __name__ == "__main__":
    file_input = "input/Example_CL_LDM.json"  
    Generator(file_input=file_input)
    print("Done")
