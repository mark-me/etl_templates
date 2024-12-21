CREATE TABLE CL.dms_table_1
(
    column_1 int  NOT NULL ,
    column_2 nvarchar  NULL 
)
WITH
(
    DISTRIBUTION = HASH ( column_1 ),
    CLUSTERED COLUMNSTORE INDEX
)
;