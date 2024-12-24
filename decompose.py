import json


class ModelObjects:
    def __init__(self, dict_pd: dict):
        self.id = dict_pd["a:ObjectID"]
        self.name = dict_pd["a:Name"]
        self.code = dict_pd["a:Code"]


class Attribute(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        print("-- Attr: " + self.name)
        if "a:Stereotype" in dict_pd:
            self.stereotype = dict_pd["a:Stereotype"]
        else:
            self.stereotype = None
        self.datatype = dict_pd["a:DataType"]
        if "a:LogicalAttribute.Mandatory" in dict_pd:
            if dict_pd["a:LogicalAttribute.Mandatory"] == 1:
                self.mandatory = True
            else:
                self.mandatory = False
        else:
            self.mandatory = False


class Entity(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        print("Entity: " + self.name)
        pd_attributes = dict_pd["c:Attributes"]["o:EntityAttribute"]
        self.dict_attributes = {}
        if isinstance(pd_attributes, list):
            for pd_attribute in pd_attributes:
                attribute = Attribute(pd_attribute)
                self.dict_attributes[attribute.id] = attribute
        elif isinstance(pd_attributes, dict):
            attribute = Attribute(pd_attributes)
            self.dict_attributes[attribute.id] = attribute


class ShortcutAttributes(ModelObjects):
    def __init__(self, dict_pd):
        super().__init__(dict_pd)
        print("-- Shortcut attr: " + self.name)


class Shortcut(ModelObjects):
    def __init__(self, dict_pd: dict):
        super().__init__(dict_pd)
        print("Shortcut: " + self.name)
        if "c:SubShortcuts" in dict_pd:
            pd_attributes = dict_pd["c:SubShortcuts"]["o:Shortcut"]
            self.dict_attributes = {}
            if isinstance(pd_attributes, list):
                for pd_attribute in pd_attributes:
                    attribute = ShortcutAttributes(pd_attribute)
                    self.dict_attributes[attribute.id] = attribute
            elif isinstance(pd_attributes, dict):
                attribute = ShortcutAttributes(pd_attribute)
                self.dict_attributes[attribute.id] = attribute


class Mapping(ModelObjects):
    def __init__(self, dict_mapping: dict, dict_pd: dict):
        super().__init__(dict_pd)
        print("Mapping: " + self.name)
        if "a:Stereotype" in dict_mapping:
            self.stereotype = dict_mapping["a:Stereotype"]
        else:
            self.stereotype = None

        id_entity = dict_mapping["c:Classifier"]["o:Entity"]["@Ref"]
        entity = dict_entities[id_entity]
        test = "me"


with open("output/example_dwh.json") as json_file:
    models = json.load(json_file)


# lst_pd_datasources = models["c:DataSources"]

# lst_pd_shortcut = models["c:Entities"]["o:Shortcut"]
# lst_pd_sourcemodels = ["c:SourceModels"]

# lst_mappings = models["c:Mappings"]
# with open("output/lst_mappings.json", "w") as fp:
#     json.dump(lst_mappings, fp, indent=4)

lst_pd_entity = models["c:Entities"]["o:Entity"]
dict_entities = {}
for pd_entity in lst_pd_entity:
    # Extract usable entity
    entity = Entity(pd_entity)
    dict_entities[entity.id] = entity

lst_pd_shortcuts = models["c:Entities"]["o:Shortcut"]
dict_shortcuts = {}
for pd_shortcut in lst_pd_shortcuts:
    shortcut = Shortcut(pd_shortcut)
    dict_shortcuts[shortcut.id] = shortcut

lst_pd_mappings = models["c:Mappings"]["o:DefaultObjectMapping"]
lst_mappings = []
for mapping in lst_pd_mappings:
    lst_mappings.append(Mapping(mapping, dict_entities))

print("Done")
