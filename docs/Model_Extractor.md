# Extracted Model from Power Designer

The result of using the pd_extractor module is a JSON representation of the model and the transformations involved to fill the model.

The model represents data structures, including models, entities, attributes, relationships, transformations, mappings, filters and functions.

The model also provides a structured way to define data elements and their transformations, including source objects, join conditions, and attribute mappings.

## Power Designer modelling functionality

Power Designer allows you to build data models. With the MDDE extension we specify how the model of a document is loaded. Below is described what what metadata on the data models is extracted and how the ETL/Transformations are extracted. Both models are represented in the JSON that results from the extraction.

### Model and Transformation representation in JSON

```mermaid
erDiagram
    MODEL ||--o{ ENTITY : contains
    ENTITY ||--o{ ATTRIBUTE : has
    ATTRIBUTE ||--o| DOMAIN : uses
    TRANSFORMATION ||--o{ MAPPING : contains
    MAPPING ||--|| ENTITY_TARGET : targets
    SOURCE_OBJECT ||--o{ ATTRIBUTE_MAPPING : sources
    SOURCE_OBJECT ||--o{ JOIN_CONDITION : defines
    MAPPING ||--o{ ATTRIBUTE_MAPPING : maps
```

### Entity Relationship diagram

This section specifies how both above are related, and not so much how they are extracted into a JSON

```mermaid
erDiagram
    MODEL ||--o{ ENTITY : contains
    ENTITY ||--o{ ATTRIBUTE : has
    ATTRIBUTE ||--o| DOMAIN : uses
    TRANSFORMATION ||--o{ MAPPING : contains
    MAPPING ||--|| ENTITY_TARGET : targets
    ENTITY_TARGET ||--|| ENTITY: role
    SOURCE_OBJECT ||--o{ ATTRIBUTE_MAPPING : sources
    SOURCE_OBJECT ||--o{ JOIN_CONDITION : defines
    JOIN_CONDITION ||--|| ATTRIBUTE: role
    SOURCE_OBJECT ||--|| ENTITY: role
    MAPPING ||--o{ ATTRIBUTE_MAPPING : maps
    ATTRIBUTE_MAPPING }o--o{ ATTRIBUTE: role
```

## Class diagram for the JSON Model structure

### Model - ER Diagram version

```mermaid
erDiagram
    Model {
        string Id   PK  "o2"
        string ObjectID     "FCC854D4-4895-4081-A2AB-FA90BEF99C2A"
        string Name     "Example CL LDM"
        string Code     "'DA_CENTRAL', Used in DDL for setting Schema name of database object."
        int Rowcount    "Estimated rowcount for the table. Needed for distribution an index part of the DDL creation."
        string CreationDate     "2024-11-29T09:27:03"
        string Creator      "User007"
        string ModificationDate "2025-01-06T15:41:54"
        string Modifier     "User007"
        string Author       "User007"
        string Version      "1.0"
        string RepositoryFilename       "Filename of the Power Designer model file."
        bool IsDocumentModel        "If true then model is working model of the file and not a reference model."
    }
    Model ||--o{ Entity : contains
    Entity {
        string Id   PK  "o10"
        string ObjectID     "73A6B276-64CF-4EBF-A0A6-A080E19C64DF"
        string Name     "Country"
        string Code     "'COUNTRY', Will be used as name for physical objects like for creation of tables."
        string CreationDate     "2024-11-29T09:36:54"
        string Creator      "User007"
        string ModificationDate
        string Modifier     "User007"
    }
    Entity ||--o{ Attribute : has
    Attribute {
        int Order        "0, The order of the attributes based on the order of attributes in a Power Designer Model."
        string Id   PK  "o90"
        string ObjectID     "9AE60148-E746-46D6-BFF3-6917112583D9"
        string Name     "Code"
        string Code     "CODE"
        string CreationDate "2024-11-29T09:37:58"
        string Creator "User007"
        string ModificationDate "2024-12-27T08:27:11"
        string Modifier "User007"
        string DataType     "'VMBT50', DataType is no Domain is selected."
        int Length  "50"
        bool IsMandatory "true"
    }
    Attribute ||--o| Domain : uses
    Domain {
        string Id   PK  "o215"
        string Name "Code"
        string Code "CODE"
        string DataType "VMBT50"
        int Length   "50"
        int Precision
    }
```

### Model - Class Diagram version

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
        +Boolean IsMandatory
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
    class ConditionComponents{
        +String LiteralValue
    }
    class ComponentAttribute{
        + String Id
        + String Name
        + String Code
        + String IdModel
        + String NameModel
        + String CodeModel
        + Boolean IsDocumentModel
        + String IdEntity
        + String NameEntity
        + String CodeEntity
        + String EntityAlias
    }
    class AttributeChild{
    }
    class AttributeParent{
    }
    class AttributeMapping {
        +String Id
        +String ObjectID
        +Integer Order
    }
    Mapping "1" *-- "1" EntityTarget
    Mapping "1" *-- "*" SourceObject
    SourceObject "1" *-- "*" JoinCondition
    JoinCondition "1" *-- "*" ConditionComponents
    ConditionComponents "1" *-- "*" AttributeChild
    ConditionComponents "1" *-- "*" AttributeParent
    ComponentAttribute <|-- AttributeChild
    ComponentAttribute <|-- AttributeParent
    Mapping "1" *-- "*" AttributeMapping
    note for Mapping "Defines data transformations"
    note for SourceObject "Source tables with join info"
    note for JoinCondition "Join criteria"
    note for ConditionComponents "The components which make op the join criteria"
    note for ComponentAttribute "A attribute as part of a join condition (component)"
    note for AttributeChild "When a ComponentAttribute plays the role of a child attribute"
    note for AttributeParent "When a ComponentAttribute plays the role of a parent attribute"
```
