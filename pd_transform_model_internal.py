import logging

import logging_config
from pd_transform_object import ObjectTransformer

logger = logging.getLogger(__name__)


class TransformModelInternal(ObjectTransformer):
    def __init__(self):
        super().__init__()

    def model(self, content: dict) -> dict:
        content = self.convert_timestamps(content)
        if "c:GenerationOrigins" in content:
            model = content["c:GenerationOrigins"]["o:Shortcut"]  # Document model
            model = self.clean_keys(model)
        else:
            lst_include = [
                "@Id",
                "@a:ObjectID",
                "a:Name",
                "a:Code",
                "a:CreationDate",
                "a:Creator",
                "a:ModificationDate",
                "a:Modifier",
                "a:PackageOptionsText",
                "a:ModelOptionsText",
                "a:Author",
                "a:Version",
                "a:RepositoryFilename",
                "a:ExtendedAttributesText",
            ]
            model = {item: content[item] for item in content if item in lst_include}
            model = self.clean_keys(model)
        model["IsDocumentModel"] = True
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

    def entities(self, lst_entities: list, dict_domains: dict) -> list:
        """Reroutes internal entity data and enriches attributes with domain data

        Args:
            lst_entities (list): The Part of the PowerDesigner document that describes entities
            dict_domains (dict): All domains (i.e. datatypes used for attributes)

        Returns:
            list: _description_
        """
        lst_entities = self.clean_keys(lst_entities)
        for i in range(len(lst_entities)):
            entity = lst_entities[i]

            # Reroute attributes
            entity = self.__entity_attributes(entity=entity, dict_domains=dict_domains)
            # Create subset of attributes to enrich identifier attributes
            dict_attrs = {
                d["Id"]: {"Name": d["Name"], "Code": d["Code"]}
                for d in entity["Attributes"]
            }

            # Identifiers and primary identifier
            entity = self.__entity_identifiers(entity=entity, dict_attrs=dict_attrs)

            # Reroute default mapping
            # TODO: research role DefaultMapping
            lst_entities[i] = entity
        return lst_entities

    def __entity_attributes(self, entity: dict, dict_domains: list) -> dict:
        """Reroutes attribute data for internal entities and enriches them with domain data

        Args:
            entity (dict): Internal entity
            dict_domains (list): All domains

        Returns:
            dict: _description_
        """
        lst_attrs = entity["c:Attributes"]["o:EntityAttribute"]
        if isinstance(lst_attrs, dict):
            lst_attrs = [lst_attrs]
        lst_attrs = self.clean_keys(lst_attrs)
        for i in range(len(lst_attrs)):
            # Change domain data
            attr = lst_attrs[i]
            attr["Order"] = i
            if "c:Domain" in attr:
                # Reroute domain data
                id_domain = attr["c:Domain"]["o:Domain"]["@Ref"]

                # Add matching domain data
                attr_domain = dict_domains[id_domain]
                keys_domain = {"Id", "Name", "Code", "DataType", "Length", "Precision"}
                attr_domain = {
                    k: attr_domain[k] for k in keys_domain if k in attr_domain
                }
                attr["Domain"] = attr_domain
                attr.pop("c:Domain")
            lst_attrs[i] = attr
        entity["Attributes"] = lst_attrs
        entity.pop("c:Attributes")
        return entity

    def __entity_identifiers(self, entity: dict, dict_attrs: dict) -> dict:
        """Reroutes the indices and primary key for an internal entity

        Args:
            entity (dict): _description_
            dict_attrs (dict): All entity attributes

        Returns:
            dict: _description_
        """
        # Set primary identifiers as an attribute of the identifiers
        has_primary = "c:PrimaryIdentifier" in entity
        if has_primary:
            primary_id = entity["c:PrimaryIdentifier"]["o:Identifier"]["@Ref"]

        # Reroute identifiers
        if "c:Identifiers" in entity:
            identifiers = entity["c:Identifiers"]["o:Identifier"]
            if isinstance(identifiers, dict):
                identifiers = [identifiers]
            identifiers = self.clean_keys(identifiers)
            # Clean and transform identifier data
            for j in range(len(identifiers)):
                identifier = identifiers[j]
                identifier["EntityID"] = entity["Id"]
                identifier["EntityName"] = entity["Name"]
                identifier["EntityCode"] = entity["Code"]
                if "c:Identifier.Attributes" not in identifier:
                    logger.error(
                        f"No attributes included in the identifier '{identifier["Name"]}'"
                    )
                else:
                    lst_attr_id = identifier["c:Identifier.Attributes"][
                        "o:EntityAttribute"
                    ]
                    if isinstance(lst_attr_id, dict):
                        lst_attr_id = [lst_attr_id]
                    lst_attr_id = [dict_attrs[d["@Ref"]] for d in lst_attr_id]
                    identifier["Attributes"] = lst_attr_id
                    identifier.pop("c:Identifier.Attributes")
                # Set primary identifier attribute
                if has_primary:
                    identifier["IsPrimary"] = primary_id == identifier["Id"]
                identifiers[j] = identifier
            entity["Identifiers"] = identifiers
            entity.pop("c:Identifiers")
            entity.pop("c:PrimaryIdentifier")
        return entity

    def relationships(self, lst_relationships: list, lst_entity: list) -> list:
        """Reroutes and enriches relationship data

        Args:
            lst_relationships (list): Power Designer items describing a relationship between entities
            lst_entity (dict): Contains all entities

        Returns:
            list: _description_
        """
        # Creating dictionaries to simplify adding data to relationships
        dict_entities = {entity["Id"]: entity for entity in lst_entity}
        dict_attributes = {
            attr["Id"]: attr for entity in lst_entity for attr in entity["Attributes"]
        }
        dict_identifiers = {
            ids["Id"]: ids
            for entity in lst_entity
            if "Identifiers" in entity
            for ids in entity["Identifiers"]
        }

        # Processing relationships
        lst_relationships = self.clean_keys(lst_relationships)
        if isinstance(lst_relationships, dict):
            lst_relationships = [lst_relationships]
        for i in range(len(lst_relationships)):
            relationship = lst_relationships[i]
            # Add entity data
            self.__relationship_entities(
                relationship=relationship, dict_entities=dict_entities
            )
            # Add attribute data
            relationship = self.__relationship_join(
                relationship=relationship, dict_attributes=dict_attributes
            )
            # Add identifier data
            relationship = self.__relationship_identifiers(
                relationship=relationship, dict_identifiers=dict_identifiers
            )
            lst_relationships[i] = relationship

        return lst_relationships

    def __relationship_entities(self, relationship: dict, dict_entities: dict) -> dict:
        """Reroutes and renames the entities the relationship describes

        Args:
            relationship (dict): The Power Designer document part that describes a relationship
            dict_entities (dict): All entities

        Returns:
            dict: The cleaned version of the relationship data
        """
        id_entity = relationship["c:Object1"]["o:Entity"]["@Ref"]
        relationship["Entity1"] = dict_entities[id_entity]
        relationship.pop("c:Object1")
        id_entity = relationship["c:Object2"]["o:Entity"]["@Ref"]
        relationship["Entity2"] = dict_entities[id_entity]
        relationship.pop("c:Object2")
        return relationship

    def __relationship_join(self, relationship: dict, dict_attributes: dict) -> dict:
        """Reroute and add entity attribute data to joins

        Args:
            relationship (dict): The relationship containing the join(s)
            dict_attributes (dict): Attributes which is used to enrich the set

        Returns:
            dict: A cleaned version of the relationship data
        """
        lst_joins = relationship["c:Joins"]["o:RelationshipJoin"]
        if isinstance(lst_joins, dict):
            lst_joins = [lst_joins]
        lst_joins = self.clean_keys(lst_joins)
        for i in range(len(lst_joins)):
            join = {}
            join["Order"] = i
            id_attr = lst_joins[i]["c:Object1"]["o:EntityAttribute"]["@Ref"]
            join["Entity1Attribute"] = dict_attributes[id_attr]
            id_attr = lst_joins[i]["c:Object2"]["o:EntityAttribute"]["@Ref"]
            join["Entity2Attribute"] = dict_attributes[id_attr]
            lst_joins[i] = join
        relationship["Joins"] = lst_joins
        relationship.pop("c:Joins")
        return relationship

    def __relationship_identifiers(
        self, relationship: dict, dict_identifiers: dict
    ) -> dict:
        lst_identifier_id = relationship["c:ParentIdentifier"]["o:Identifier"]
        if isinstance(lst_identifier_id, dict):
            lst_identifier_id = [lst_identifier_id]
        relationship["Identifiers"] = [
            dict_identifiers[id["@Ref"]] for id in lst_identifier_id
        ]
        relationship.pop("c:ParentIdentifier")
        return relationship
