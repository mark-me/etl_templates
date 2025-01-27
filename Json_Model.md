## Opbouw
* Model 
    * Entities
        * Attributes
            * Domain
        * Identifiers
            * Attribute
        * RolePlayViews


* Tranformation
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
* Models 
    * Model 
        * Id: "o2"
        * Name: "Douane CL LDM"
        * Code: "DA_CENTRAL"
        * CreationDate: "2024-11-29T09:27:03"
        * Creator: "Wouter"
        * ModificationDate: "2025-01-06T15:41:54"
        * Author: "Klaas"
        * Modifier: "Jan"
        * Version: "1.0"
        * IsDocumentModel: true
        * Entities:
            * Entity:
                * Id: "o10"
                * ObjectID: "73A6B276-64CF-4EBF-A0A6-A080E19C64DF"
                * Name: "Country"
                * Code: "COUNTRY"
                * Schema: "DA_CENTRAL"
                * CreationDate: "2024-11-29T09:36:54"
                * Creator: "Wouter"
                * ModificationDate: "2025-01-06T14:18:59"
                * Modifier: "Jan"
                * Rowcount: "300"
                * Attributes:
                    * Attribute:
                        * Order": 0
                        * Id: "o1210"
                        * ObjectID: "73A6B276-64CF-4EBF-A0A6-A080E19C5432"
                        * Name: "Code"
                        * Code: "CODE"
                        * CreationDate: "2024-11-29T09:37:58"
                        * Creator: "Wouter"
                        * ModificationDate: "2024-12-27T08:27:11"
                        * Modifier: "Jan"
                        * DataType: "VMBT50"
                        * Length: "50"
                        * Mandatory: "1"
                        * Domain:
                            * Id: "o215"
                            * Name: "Code"
                            * Code: "CODE"
                            * DataType: "VMBT50"
                            * Length: "50"
                * Identifiers:
                    * Identifier:
                        * Id: "o214"
                        * ObjectID: "DE9826EC-23AF-4137-8858-BFBE0768723A"
                        * Name: "Country"
                        * Code: "COUNTRY"
                        * CreationDate: "2024-11-29T15:31:15"
                        * Creator: "Wouter"
                        * ModificationDate: "2024-11-29T16:15:10"
                        * Modifier: "Jan"
                        * EntityID: "o10"
                        * EntityName: "Country"
                        * EntityCode: "COUNTRY"
                        * Attributes:
                            * Name: "Code"
                            * Code: "CODE"
                        * IsPrimary: true
                * RolePlayViews:
                    * RolePlayView
                        * Id: "o229"
                        * ObjectID: "B63919EA-749D-4681-A12C-49695B3A19F4"
                        * Name: "Land van verzending"
                        * Code: "LANDVANVERZENDING"
                        * CreationDate: "2024-12-23T11:57:09"
                        * Creator: "pollj04"
                        * ModificationDate: "2024-12-23T11:57:22"
                        * Modifier: "pollj04"
                        * Stereotype: "DOU_RolePlayingViewsData"

* Tranformations: 
    * Mappings:
        * Mapping:
            * Id: "o122"
            * ObjectID: "87BC5C63-ACC3-4F7A-89DB-2461009943D6"
            * Name: "DMS"
            * Code: "DMS"
            * CreationDate": "2024-12-27T09:19:54"
            * Creator": "Jan"
            * ModificationDate": "2024-12-27T11:53:12"
            * Modifier": "Eric"
            * EntityTarget: 
                * Id: "o14"
                * Name: "DocumentDeclaration"
                * Code: "DOCUMENT_DECLARATION"
                * IdModel: "o2"
                * NameModel: "Douane CL LDM"
                * CodeModel: "DA_CENTRAL"
                * IsDocumentModel": true
            * SourceObjects (mdde_SourceObjects)
                * SourceObject:
                    * Order": 0
                    * Id: "o124",
                    * ObjectID: "2DBCCF9E-A133-48A4-91E8-59EE0D3E2CAD",
                    * Name: "DECLARTN dcl",
                    * Code: "DECLARTN_DCL",
                    * CreationDate: "2024-12-27T09:19:54",
                    * Creator: "pollj04",
                    * ModificationDate: "2024-12-27T09:26:52",
                    * Modifier: "pollj04",
                    * Stereotype: "mdde_SourceObject",
                    * JoinType: "FROM"  (From ExtendedAttributesText)    
                    * JoinAlias: "dcl"  (From ExtendedAttributesText)    
                    * Entity: 
                        * Id: "o126",
                        * Name: "DECLARTN",
                        * Code: "DECLARTN",
                        * IdModel: "o352",
                        * NameModel: "IN_DMS (LDM)",
                        * CodeModel: "IN_DMS__LDM_",
                        * IsDocumentModel: false
                    * JoinConditions
                        * JoinCondition
                            * Order: 0
                            * Id: "o131"
                            * ObjectID: "EA3AA547-A061-4056-936E-4DD987865CCF"
                            * Name: "Join condition_1"
                            * Code: "JOIN_CONDITION_1"
                            * Operator: "="
                            * CreationDate: "2024-12-27T09:20:52"
                            * Creator: "pollj04"
                            * ModificationDate: "2025-01-02T10:35:08"
                            * Modifier: "pollj04"
                            * Stereotype: "mdde_JoinCondition"
                            * ParentIsLiteralValue: false
                            * AttributeChild: 
                                    * Id: "o133",
                                    * Name""DECL_REFE"
                                    * Code: "DECL_REFE"
                                    * IdModel: "o352"
                                    * NameModel: "IN_DMS (LDM)"
                                    * CodeModel: "IN_DMS__LDM_"
                                    * IdEntity: "o129"
                                    * NameEntity: "PRCSSTUS"
                                    * CodeEntity: "PRCSSTUS"
                            * AttributeParent: 
                                    "Id": "o136",
                                    "Name": "REFE",
                                    "Code": "REFE",
                                    "IdModel": "o352",
                                    "NameModel": "IN_DMS (LDM)",
                                    "CodeModel": "IN_DMS__LDM_",
                                    "IdEntity": "o126",
                                    "NameEntity": "DECLARTN",
                                    "CodeEntity": "DECLARTN",
                                    "EntityAlias": "o124"
                        * JoinCondition
                            * Order: 0
                            * Id: "o137"
                            * ObjectID: "62662D3C-373D-41D6-9C6F-53582026D713"
                            * Name: "Join condition_2"
                            * Code: "JOIN_CONDITION_2"
                            * Operator: "<>"
                            * CreationDate: "2024-12-27T09:20:52"
                            * Creator: "pollj04"
                            * ModificationDate: "2025-01-02T10:35:08"
                            * Modifier: "pollj04"
                            * Stereotype: "mdde_JoinCondition"
                            * ParentIsLiteralValue: true
                            * AttributeChild: 
                                    * Id: "o139",
                                    * Name""TYPE"
                                    * Code: "TYPE"
                                    * IdModel: "o352"
                                    * NameModel: "IN_DMS (LDM)"
                                    * CodeModel: "IN_DMS__LDM_"
                                    * IdEntity: "o129"
                                    * NameEntity: "PRCSSTUS"
                                    * CodeEntity: "PRCSSTUS"
                            * LiteralValue: "1"
            * AttributeMappings
                * AttributeMapping:
                    * Order: 0,
                    * Id: "o147",
                    * ObjectID: "9208FE51-3D08-456A-B85B-5AE7620B8E06",
                    * CreationDate: "2024-12-27T09:20:52",
                    * Creator: "pollj04",
                    * ModificationDate: "2024-12-27T09:26:52",
                    * Modifier: "pollj04",
                    * AttributesSource:
                        * Id: "o149"
                        * Name: "TID"
                        * Code: "TID"
                        * IdModel: "o352"
                        * NameModel: "IN_DMS (LDM)"
                        * CodeModel: "IN_DMS__LDM_"
                        * IdEntity: "o126"
                        * NameEntity: "DECLARTN"
                        * CodeEntity: "DECLARTN"
                        * EntityAlias: "o124"
                    * AttributeTarget": 
                        * Id: "o150"
                        * Name: "DocumentDeclarationNumber"
                        * Code: "DOCUMENTDECLARATIONNUMBER"
                        * IdModel: "o2"
                        * NameModel: "Douane CL LDM"
                        * CodeModel: "DA_CENTRAL"
                        * IdEntity: "o14"
                        * NameEntity: "DocumentDeclaration"
                        * CodeEntity: "DOCUMENT_DECLARATION"
                * AttributeMapping:
                    * Order": 1
                    * Id: "o154"
                    * ObjectID: "38FCF844-672E-4733-B024-4800337D6EDA"
                    * CreationDate: "2024-12-27T09:20:52"
                    * Creator: "pollj04"
                    * ModificationDate: "2024-12-27T09:26:52"
                    * Modifier: "pollj04"
                    * Expression: "'N/A'"
                    * AttributeTarget: 
                        * Id: "o155",
                        * Name: "DocumentDeclarationFileNumber",
                        * Code: "DOCUMENTDECLARATIONFILENUMBER",
                        * IdModel: "o2",
                        * NameModel: "Douane CL LDM",
                        * CodeModel: "DA_CENTRAL",
                        * IsDocumentModel: false,
                        * IdEntity: "o14",
                        * NameEntity: "DocumentDeclaration",
                        * CodeEntity: "DOCUMENT_DECLARATION"


                    

                    
 
 