CREATE TABLE CL.dms_table_2
(
    column_3 int  NOT NULL ,
    column_4 datetime  NULL )
WITH
(
    DISTRIBUTION = HASH ( column_3 ),
    CLUSTERED COLUMNSTORE INDEX
)
;