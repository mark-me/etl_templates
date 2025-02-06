## Opbouw
* Model(s)
    * Entities
        * Attributes
            * Domain
        * Identifiers
            * Attribute
        * 
    * Relationships


* Transformations
    * Mappings:
        * Mapping:
            * EntityTarget: 
                * SourceObjects (mdde_SourceObjects)
                    * SourceObject:
                        * Entity: 
                        * JoinConditions (mdde_JoinCondition)
                            * JoinCondition
                                * AttributeChild
                                * AttributeParent
                                * LiteralValue
            * AttributeMapping
                * Expression
                * AttributesSource
                * AttributeTarget
    * Filters
        * Filter:
            * Expression:
            * Attributes
                * Domain
    * Pivot
    * Agg
    * Functions
        Function
            * Expression:
            * Attributes
                * Domain

    
## Voorbeeld
JSON
----

```json
{
    // Models --> list of models that are present in a Power Designer model file.
    "Models": [
		// Model --> Dict that present in single model with the data needed to generate a DDL
        {
            "Id": "o2",
            "ObjectID": "FCC854D4-4895-4081-A2AB-FA90BEF99C2A",
            "Name": "Example CL LDM",
            // Model Code  --> Used in DDL for setting Schema name of database object.
            "Code": "DA_CENTRAL",
            // Rowcount --> Estimated rowcount for the table. Needed for distribution an index part of the DDL creation. 
			"Rowcount": "300",
            "CreationDate": "2024-11-29T09:27:03",
            "Creator": "User007",
            "ModificationDate": "2025-01-06T15:41:54",
            "Modifier": "User007",
            "Author": "User007",
            "Version": "1.0",
            // RepositoryFilename --> Filename of the Power Designer model file.
            "RepositoryFilename": "C:\\Users\\User007\\PowerDesigner\\Models\\Example.ldm",
            // IsDocumentModel --> if == true then, model is working model of the file and not a reference model
            "IsDocumentModel": true,
            // Entities --> list of Entities present in the model
            "Entities": [
                // Entity --> dict of a Entity 
				{
                    "Id": "o10",
                    "ObjectID": "73A6B276-64CF-4EBF-A0A6-A080E19C64DF",
                    "Name": "Country",
                    // Code --> Will be used as name for physical objects like for creation of tables
                    "Code": "COUNTRY",
                    "CreationDate": "2024-11-29T09:36:54",
                    "Creator": "User007",
                    "ModificationDate": "2025-01-06T14:18:59",
                    "Modifier": "User007",
                    // Attributes --> List of Attributes for a Entity (Columns)
                    "Attributes": [
						{
                            // Attribute --> a Attribute for of a Entity (Column)
                            // Order --> a Attribute to use the correct order of the attributes based on the order of attributes in a Power Designer Model.
                            "Order": 0,
							"Id": "o90",
                            "ObjectID": "9AE60148-E746-46D6-BFF3-6917112583D9",
                            "Name": "Code",
                            "Code": "CODE",
                            "CreationDate": "2024-11-29T09:37:58",
                            "Creator": "User007",
                            "ModificationDate": "2024-12-27T08:27:11",
                            "Modifier": "User007",
                            // DataType --> DataType is no Domain is selected.
                            "DataType": "VMBT50",
                            "Length": "50",
                            "LogicalAttribute.Mandatory": "1",
                            // Domain --> Dict of a pre-defined datatype for the attribute 
                            "Domain": {
                                "Id": "o215",
                                "Name": "Code",
                                "Code": "CODE",
                                "DataType": "VMBT50",
                                "Length": "50",
                                "Precision": ""
                            }
                        }
                    ]    
                }
            ]
        }
    ],
    // Transformations --> Dict of objects that are not part of the core model. (Mappings, Filters, Scaler, Pivot, Aggregations)
    "transformations": 
        {
            // Mappings --> List of Mappings 
            "Mappings": [
                {
                    // Mapping --> Dict with a Mapping for a entity
                    "Id": "o18",
                    "ObjectID": "E006B5A6-C7FB-417B-8CC6-A4A8AA58B3C2",
                    "Name": "DTO",
                    "Code": "DTO",
                    "CreationDate": "2024-11-29T15:10:19",
                    "Creator": "User007",
                    "ModificationDate": "2025-01-06T14:18:59",
                    "Modifier": "User007",
                    // EntityTarget --> Dict with info of the target entity for this mapping.
                    "EntityTarget": {
                        "Id": "o10",
                        "Name": "Country",
                        "Code": "COUNTRY",
                        "IdModel": "o2",
                        "NameModel": "Douane CL LDM",
                        "CodeModel": "DA_CENTRAL",
                        "IsDocumentModel": true
                    },
                    // SourceObjects --> List of source entities(tabels) and the role of the entity (From, Join, Apply)
                    "SourceObjects": [
                        // SourceObject --> Dict of a Source object. Depending on the JoinType  structure can vary. Two examples are present in this example 
                        {
                            // Order --> The order that the jointype need to be implemented. "From" should always be the first one.
                            "Order": 0,
                            "Id": "o20",
                            "EntityAlias": "o20",
                            "ObjectID": "0D8A51C8-13BC-4AAC-A7F0-1718171ECF78",
                            "Name": "ELEMENT Land",
                            "Code": "ELEMENT_LAND",
                            "CreationDate": "2024-11-29T15:10:19",
                            "Creator": "User007",
                            "ModificationDate": "2025-01-06T14:18:56",
                            "Modifier": "User007",
                            "JoinType": "FROM",
                            "JoinAlias": "Land",
                            // Entity --> Dict of the source entitie en the model info for the JoinType
                            "Entity": {
                                "Id": "o22",
                                "Name": "ELEMENT",
                                "Code": "ELEMENT",
                                "IdModel": "o307",
                                "NameModel": "IN_DTO (LDM)",
                                "CodeModel": "IN_DTO",
                                "IsDocumentModel": false
                            }                        
                        },
                        // SourceObject --> Dict of a Source object with JoinType "Left Join". For a Join there needs to be a condition for the join. This can be "LiteralValue" or a Entity/Attribute.
                        {
                            "Order": 1,
                            "Id": "o23",
                            "EntityAlias": "o23",
                            "ObjectID": "4D98CB2F-99C1-4297-B548-283E36D240DA",
                            "Name": "ELEMENT LandNaamEN",
                            "Code": "ELEMENT_LANDNAAMEN",
                            "CreationDate": "2024-11-29T15:10:32",
                            "Creator": "User007",
                            "ModificationDate": "2024-12-23T13:49:49",
                            "Modifier": "User007",
                            "JoinType": "LEFT JOIN",
                            "JoinAlias": "LandNaamEN",
                            // Entity --> Dict of the source entitie en the model info for the JoinType
                            "Entity": {
                                "Id": "o22",
                                "Name": "ELEMENT",
                                "Code": "ELEMENT",
                                "IdModel": "o307",
                                "NameModel": "IN_DTO (LDM)",
                                "CodeModel": "IN_DTO",
                                "IsDocumentModel": false
                            },
                            // JoinConditions --> List of the Conditions for the Join
                            "JoinConditions": [
                                // JoinCondition --> Dict With a example of a condition containing a LiteralValue
                                {
                                    "Order": 0,
                                    "Id": "o26",
                                    "ObjectID": "9FFDA3CA-7455-4CAC-96F9-AFF8D247E0F6",
                                    "Name": "Join condition_1",
                                    "Code": "JOIN_CONDITION_1",
                                    "CreationDate": "2024-11-29T15:11:33",
                                    "Creator": "User007",
                                    "ModificationDate": "2024-11-29T15:15:08",
                                    "Modifier": "User007",
                                    // JoinOperator --> gives the type of the comparison (=, >, <, <>, <=, etc. )
                                    "JoinOperator": "=",
                                    // JoinComponents --> Dict With the objects needed for the comparison. This is a example of a comparison between a attribute value and a LiteralValue 
                                    "JoinComponents ": {
                                        "LiteralValue": "'M01'",
                                        "AttributeChild": {
                                            "Id": "o28",
                                            "Name": "TABNR_8",
                                            "Code": "TABNR_8",
                                            "IdModel": "o307",
                                            "NameModel": "IN_DTO (LDM)",
                                            "CodeModel": "IN_DTO",
                                            "IsDocumentModel": false,
                                            "IdEntity": "o22",
                                            "NameEntity": "ELEMENT",
                                            "CodeEntity": "ELEMENT"
                                        }
                                    }
                                },
                                // JoinCondition --> Dict With a example of a condition containing Entity/Attribute
                                {
                                    "Order": 1,
                                    "Id": "o29",
                                    "ObjectID": "5EEA9334-7050-460E-AB17-D4F00A2809F9",
                                    "Name": "Join condition_2",
                                    "Code": "JOIN_CONDITION_2",
                                    "CreationDate": "2024-11-29T15:11:33",
                                    "Creator": "User007",
                                    "ModificationDate": "2024-11-29T15:15:08",
                                    "Modifier": "User007",
                                    // JoinOperator --> gives the type of the comparison (=, >, <, <>, <=, etc. )
                                    "JoinOperator": "=",
                                    // JoinComponents --> Dict With the objects needed for the comparison. This is a example of a comparison between the destination attribute value and the source attribute value 
                                    "JoinComponents": {
                                        "AttributeChild": {
                                            "Id": "o31",
                                            "Name": "ELEMKD",
                                            "Code": "ELEMKD",
                                            "IdModel": "o307",
                                            "NameModel": "IN_DTO (LDM)",
                                            "CodeModel": "IN_DTO",
                                            "IsDocumentModel": false,
                                            "IdEntity": "o22",
                                            "NameEntity": "ELEMENT",
                                            "CodeEntity": "ELEMENT",
                                            "EntityAlias": "o23" //ID of Join of Entity "ELEMENT" with Alias  "LandNaamEN"
                                        },
                                        "AttributeParent": {
                                            "Id": "o31",
                                            "Name": "ELEMKD",
                                            "Code": "ELEMKD",
                                            "IdModel": "o307",
                                            "NameModel": "IN_DTO (LDM)",
                                            "CodeModel": "IN_DTO",
                                            "IsDocumentModel": false,
                                            "IdEntity": "o22",
                                            "NameEntity": "ELEMENT",
                                            "CodeEntity": "ELEMENT",
                                            "EntityAlias": "o20" //ID of From of Entity "ELEMENT" with Alias  "Land"
                                        }
                                    }
                                },
   "AttributeMapping": [
      {
         "Id": "o88",
         "ObjectID": "9CBA3030-B6C2-4377-89B9-081775CFB372",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:22:44",
         "Modifier": "pollj04",
         "Order": 0,
         "AttributeTarget": {
            "Id": "o90",
            "Name": "Code",
            "Code": "CODE",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o31",
            "Name": "ELEMKD",
            "Code": "ELEMKD",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT",
            "EntityAlias": "o61",
            "EntityAliasName": "EU"
         }
      },
      {
         "Id": "o91",
         "ObjectID": "70E42ED1-1EFB-46DC-A712-1E9972095DAA",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:23:49",
         "Modifier": "pollj04",
         "Order": 1,
         "AttributeTarget": {
            "Id": "o94",
            "Name": "NameShortNL",
            "Code": "NAMESHORTNL",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o93",
            "Name": "OMSCHR_K",
            "Code": "OMSCHR_K",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT"
         }
      },
      {
         "Id": "o95",
         "ObjectID": "C03FF812-4560-4BA7-A750-6AC7F466DBFD",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:23:49",
         "Modifier": "pollj04",
         "Order": 2,
         "AttributeTarget": {
            "Id": "o97",
            "Name": "NameShortEN",
            "Code": "NAMESHORTEN",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o93",
            "Name": "OMSCHR_K",
            "Code": "OMSCHR_K",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT"
         }
      },
      {
         "Id": "o98",
         "ObjectID": "45610586-89FC-4761-9041-C5C164EC878C",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:23:49",
         "Modifier": "pollj04",
         "Order": 3,
         "AttributeTarget": {
            "Id": "o101",
            "Name": "NameNL",
            "Code": "NAMENL",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o100",
            "Name": "OMSCHR_L",
            "Code": "OMSCHR_L",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT"
         }
      },
      {
         "Id": "o102",
         "ObjectID": "9A75FA98-1A23-4FDA-9A87-7CB265945A8F",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:23:49",
         "Modifier": "pollj04",
         "Order": 4,
         "AttributeTarget": {
            "Id": "o104",
            "Name": "NameEN",
            "Code": "NAMEEN",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o100",
            "Name": "OMSCHR_L",
            "Code": "OMSCHR_L",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT"
         }
      },
      {
         "Id": "o105",
         "ObjectID": "B38E770F-B60D-47DB-A725-6EC2FC3B293B",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:29:10",
         "Modifier": "pollj04",
         "Order": 5,
         "AttributeTarget": {
            "Id": "o108",
            "Name": "DescriptionLegal",
            "Code": "DESCRIPTIONLEGAL",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o107",
            "Name": "OMSCHR_W",
            "Code": "OMSCHR_W",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT"
         }
      },
      {
         "Id": "o109",
         "ObjectID": "E08BE1CC-F286-4359-98FA-1159F137EA21",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:26:21",
         "Modifier": "pollj04",
         "Order": 6,
         "AttributeTarget": {
            "Id": "o111",
            "Name": "PartOfEU",
            "Code": "PARTOFEU",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o31",
            "Name": "ELEMKD",
            "Code": "ELEMKD",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT",
            "EntityAlias": "o61",
            "EntityAliasName": "EU"
         }
      },
      {
         "Id": "o112",
         "ObjectID": "AFF6493B-5429-4A2D-8CCE-FF346C2ECC7B",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:29:21",
         "Modifier": "pollj04",
         "Expression": "'N/A'",
         "Order": 7,
         "AttributeTarget": {
            "Id": "o113",
            "Name": "ContinentNameNL",
            "Code": "CONTINENTNAMENL",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         }
      },
      {
         "Id": "o114",
         "ObjectID": "1E9AA765-DF46-49B3-9F3D-2BAB5057E803",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:29:21",
         "Modifier": "pollj04",
         "Expression": "'N/A'",
         "Order": 8,
         "AttributeTarget": {
            "Id": "o115",
            "Name": "ContinentNameEN",
            "Code": "CONTINENTNAMEEN",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         }
      },
      {
         "Id": "o116",
         "ObjectID": "C5E65768-2B52-47D7-A536-56080C8478B2",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:26:21",
         "Modifier": "pollj04",
         "Order": 9,
         "AttributeTarget": {
            "Id": "o118",
            "Name": "ValidFrom",
            "Code": "VALIDFROM",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o36",
            "Name": "INGDAT",
            "Code": "INGDAT",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT",
            "EntityAlias": "o61",
            "EntityAliasName": "EU"
         }
      },
      {
         "Id": "o119",
         "ObjectID": "15DB7586-8DC1-4013-AF67-45E8E5D248A4",
         "CreationDate": "2024-11-29T15:18:11",
         "Creator": "pollj04",
         "ModificationDate": "2024-11-29T15:26:21",
         "Modifier": "pollj04",
         "Order": 10,
         "AttributeTarget": {
            "Id": "o121",
            "Name": "ValidTo",
            "Code": "VALIDTO",
            "IdModel": "o2",
            "NameModel": "Douane CL LDM",
            "CodeModel": "DA_CENTRAL",
            "IsDocumentModel": false,
            "IdEntity": "o10",
            "NameEntity": "Country",
            "CodeEntity": "COUNTRY"
         },
         "AttributesSource": {
            "Id": "o41",
            "Name": "LDGDAT",
            "Code": "LDGDAT",
            "IdModel": "o307",
            "NameModel": "IN_DTO (LDM)",
            "CodeModel": "IN_DTO",
            "IsDocumentModel": true,
            "IdEntity": "o22",
            "NameEntity": "ELEMENT",
            "CodeEntity": "ELEMENT",
            "EntityAlias": "o61",
            "EntityAliasName": "EU"
         }
      }
   ]
}
```