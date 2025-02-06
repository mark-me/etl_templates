# Model

Comprehensive JSON model for representing data structures, including models, entities, attributes, relationships, transformations, mappings, filters, and functions. The model provides a structured way to define data elements and their transformations, including source objects, join conditions, and attribute mappings.

## Entity Relationship diagram for the JSON Model

```mermaid
erDiagram
    MODEL ||--o{ ENTITY : contains
    ENTITY ||--o{ ATTRIBUTE : has
    ATTRIBUTE ||--o| DOMAIN : uses
    MODEL ||--o{ TRANSFORMATION : has
    TRANSFORMATION ||--o{ MAPPING : contains
    MAPPING ||--|| ENTITY_TARGET : targets
    MAPPING ||--o{ SOURCE_OBJECT : sources
    SOURCE_OBJECT ||--o{ JOIN_CONDITION : defines
    MAPPING ||--o{ ATTRIBUTE_MAPPING : maps
```

## Class diagram for the JSON Model structure

```mermaid
classDiagram
    class Model {
        +String Id
        +String ObjectID
        +String Name
        +String Code
        +String Rowcount
        +String CreationDate
        +String Creator
        +String ModificationDate
        +String Modifier
        +String Author
        +String Version
        +String RepositoryFilename
        +Boolean IsDocumentModel
    }
    class Entity {
        +String Id
        +String ObjectID
        +String Name
        +String Code
        +String CreationDate
        +String Creator
        +String ModificationDate
        +String Modifier
    }
    class Attribute {
        +Integer Order
        +String Id
        +String ObjectID
        +String Name
        +String Code
        +String DataType
        +String Length
        +String LogicalAttribute.Mandatory
    }
    class Domain {
        +String Id
        +String Name
        +String Code
        +String DataType
        +String Length
        +String Precision
    }
    Model "1" *-- "*" Entity
    Entity "1" *-- "*" Attribute
    Attribute "1" o-- "0..1" Domain
    note for Model "Root container for data structures"
    note for Entity "Represents database tables"
    note for Attribute "Represents table columns"
    note for Domain "Defines data types"
```

## Class diagram for the Transformation structure

```mermaid
classDiagram
    class Mapping {
        +String Id
        +String ObjectID
        +String Name
        +String Code
        +String CreationDate
        +String Creator
        +String ModificationDate
        +String Modifier
    }
    class EntityTarget {
        +String Id
        +String Name
        +String Code
        +String IdModel
        +String NameModel
        +String CodeModel
        +Boolean IsDocumentModel
    }
    class SourceObject {
        +Integer Order
        +String Id
        +String EntityAlias
        +String ObjectID
        +String Name
        +String Code
        +String JoinType
        +String JoinAlias
    }
    class JoinCondition {
        +Integer Order
        +String Id
        +String ObjectID
        +String Name
        +String Code
        +String JoinOperator
    }
    class AttributeMapping {
        +String Id
        +String ObjectID
        +Integer Order
    }
    Mapping "1" *-- "1" EntityTarget
    Mapping "1" *-- "*" SourceObject
    SourceObject "1" *-- "*" JoinCondition
    Mapping "1" *-- "*" AttributeMapping
    note for Mapping "Defines data transformations"
    note for SourceObject "Source tables with join info"
    note for JoinCondition "Join criteria"
```