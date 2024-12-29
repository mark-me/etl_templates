class PDDocument:
    file
    models = [Model]


class Model:
    id
    name
    target_id
    Entities


class ModelObject:
    id
    name
    code


class Attribute(ModelObject):
    id_parent
    name_parent


class Entity(ModelObject):
    attributes = [Attribute]


class Relationship(ModelObject):
    entity1 = [Entity]
    entity2 = [Entity]
    entity1_attributes = [Attribute]
    entity2_attributes = [Attribute]
    entity1_to_entity2_role
    entity2_to_entity1_role
    entity1_to_entity2_cardinality
    entity2_to_entity1_cardinality


class Domain(ModelObject):
    datatype
    length
    precision


class ModelAttribute(Attribute):
    datatype
    length
    precision
    is_mandatory
    stereotype
    domain = Domain


class Indentifiers(ModelObject):
    attributes = [ModelAttribute]
    is_primary


class ModelEntity(ModelAttribute):
    attributes = [ModelAttribute]
    identifiers = [Indentifiers]


class CompositionObject(ModelObject):  # <c:ExtendedComposition.Content>
    def __init__(self, parent_id):
        super().__init__()

    stereotype
    composition_clause                      # <a:ExtendedAttributesText>
    alias = self.id
    clause_entity = Entity                  # <"o:ExtendedCollection"> for all composition_clause
    parent_alias = id                       # <"o:ExtendedCollection"> for JOIN composition_clause
    clause_attributes = [ModelAttribute]    # <"o:ExtendedCollection"> for JOIN composition_clause
    parent_attributes = [ModelAttribute]    # <"o:ExtendedCollection"> for JOIN composition_clause


class Composition(): # In case of multiple mappings?
    dict_compositions = {}
    composition_order = []
    for composition_object in composition_objects:
        composition = CompositionObject(parent_id=composition_order[-1])
        composition_order.append(composition.id)
        dict_compositions[composition.id] = composition


class AttributeMapping:                 # DefaultStructuralFeatureMapping
    composition = Composition
    attribute_target = Attribute        # ExtendedSubObject
    attribute_sources = [Attribute]     # SourceFeatures ? use it here?


class Mapping(ModelObject):
    stereotype                      # (mdde_ForHorizontalLineage)
    DataSources                     # DataSource: Reference to all other models?
    target_entity = Entity          # Classifier
    source_entities = [Entity]      # SourceClassifiers
    compositions = [Composition]    # In case of multiple mappings?



