import logging

import src.log_config.logging_config as logging_config
from pd_transform_object import ObjectTransformer

logger = logging.getLogger(__name__)


class TransformModelPhysical(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def model(self, content: dict) -> dict:
        content = self.convert_timestamps(content)
        content = self.clean_keys(content)
        lst_include = [
            "Id",
            "ObjectID",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
            #"a:PackageOptionsText",
            #"a:ModelOptionsText",
            "Author",
            "Version",
            #"a:RepositoryFilename",
            #"a:ExtendedAttributesText",
        ]
        model = {item: content[item] for item in content if item in lst_include}
        return model

    def domains(self, lst_domains: list) -> dict:
        dict_domains = {}
        if isinstance(lst_domains, dict):
            lst_domains = [lst_domains]
        lst_domains = self.convert_timestamps(lst_domains)
        lst_domains = self.clean_keys(lst_domains)
        for domain in lst_domains:
            dict_domains[domain["Id"]] = domain
        return dict_domains


    def tables(self, lst_tables: list, dict_domains: dict) -> list:
        """Reroutes table data and enriches columns with domain data

        Args:
            lst_tables (list): The Part of the PowerDesigner document that describes tables
            dict_domains (dict): All domains (i.e. datatypes used for columns)

        Returns:
            list: _description_
        """
        lst_tables = self.clean_keys(lst_tables)
        for i in range(len(lst_tables)):
            table = lst_tables[i]
            lst_include = [
                "Id",
                "ObjectID",
                "Name",
                "Code",
                "Rowcount",  # Number in PD
                "CreationDate",
                "Creator",
                "ModificationDate",
                "Modifier",
                "c:Columns",
            ]
            if 'Number' in table:
                table['Rowcount']= table.pop('Number')
            else:
                table['Rowcount'] = 0
            table = {item: table[item] for item in table if item in lst_include}

            # Reroute columns
            table = self.__table_columns(table=table, dict_domains=dict_domains)

            # Clean table
            # table.pop("c:ClusterObject")

            # Reroute default mapping
            # TODO: research role DefaultMapping
            lst_tables[i] = table
        return lst_tables

    def view(self, lst_view: list) -> list:
        # content = self.convert_timestamps(content)
        lst_view = self.clean_keys(lst_view)
        lst_include = [
            "Id",
            "ObjectID",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
            "Author",
            "SQLQuery",
        ]

        lst_view_new = []
        for view in lst_view:
            # Rename to remove dot in name
            view['SQLQuery']= view.pop('View.SQLQuery')
            dict_new = {}
            for item in view.keys() :
                if item in lst_include:
                    dict_new[item] = view[item]
                    #TO DO: Model Code gebruiken als Schema Naam.
                    #dict_new.update({"Schema": "DA_Central"})
            lst_view_new.append(dict_new)
        return lst_view_new

    def procs(self, lst_procs: list) -> list:
        lst_procs = self.clean_keys(lst_procs)

        lst_include = [
            "Id",
            "ObjectID",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
            "Author",
            "BeginScript",
        ]

        lst_procs_new = []
        for procs in lst_procs:
            dict_new = {}
            for proc in procs.keys() :
                if proc in lst_include:
                    dict_new[proc] = procs[proc]
                    #TO DO: Model Code gebruiken als Schema Naam.
                    dict_new.update({"Schema": "DA_Central"})
            lst_procs_new.append(dict_new)
        return lst_procs_new

    def __table_columns(self, table: dict, dict_domains: list) -> dict:
        """Reroutes column data for columns and enriches them with domain data

        Args:
            table (dict): table
            dict_domains (list): All domains

        Returns:
            dict: _description_
        """
        lst_columns = table["c:Columns"]["o:Column"]
        if isinstance(lst_columns, dict):
            lst_columns = [lst_columns]
        lst_columns = self.clean_keys(lst_columns)
        for i in range(len(lst_columns)):
            # Change domain data
            column = lst_columns[i]
            column["Order"] = i
            if "c:Domain" in column:
                # Reroute domain data
                id_domain = column["c:Domain"]["o:Domain"]["@Ref"]

                # Add matching domain data
                column_domain = dict_domains[id_domain]
                keys_domain = {"Id", "Name", "Code", "DataType", "Length", "Precision"}
                attr_domain = {
                    k: attr_domain[k] for k in keys_domain if k in attr_domain
                }
                column["Domain"] = attr_domain
                column.pop("c:Domain")
            lst_columns[i] = column
        table["Columns"] = lst_columns
        table.pop("c:Columns")
        return table

#TODO: Clean up code
class TransformProcedures(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def procs(self, lst_procs: list) -> list:
        lst_procs = self.clean_keys(lst_procs)

        lst_include = [
            "Id",
            "ObjectID",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
            "Author",
            "BeginScript",
        ]

        lst_procs_new = []
        for procs in lst_procs:
            dict_new = {}
            for proc in procs.keys() :
                if proc in lst_include:
                    dict_new[proc] = procs[proc]
                    #TO DO: Model Code gebruiken als Schema Naam.
                    dict_new.update({"Schema": "DA_Central"})
            lst_procs_new.append(dict_new)
        return lst_procs_new

#TODO: Clean up code
class TransformViews(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def view(self, lst_view: list) -> list:
        # content = self.convert_timestamps(content)
        lst_view = self.clean_keys(lst_view)
        lst_include = [
            "Id",
            "ObjectID",
            "Name",
            "Code",
            "CreationDate",
            "Creator",
            "ModificationDate",
            "Modifier",
            "Author",
            "SQLQuery",
        ]

        lst_view_new = []
        for view in lst_view:
            # Rename to remove dot in name
            view['SQLQuery']= view.pop('View.SQLQuery')
            dict_new = {}
            for item in view.keys() :
                if item in lst_include:
                    dict_new[item] = view[item]
                    #TO DO: Model Code gebruiken als Schema Naam.
                    #dict_new.update({"Schema": "DA_Central"})
            lst_view_new.append(dict_new)
        return lst_view_new

#TODO: Clean up code
class TransformDomains(ObjectTransformer):
    def __init__(self):
        super().__init__()
