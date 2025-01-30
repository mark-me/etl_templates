CREATE TABLE [{{item.Schema}}].[{{item.Code}}]
(
{% for column in item.Columns %}
    [{{column.Name}}] {{column.DataType}}
    {%- if not loop.last -%}
        ,
    {% endif %}
{% endfor %}

)
{% if item.Rowcount|int < 10000000 %}
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    HEAP
)
;
{% endif %}
                            
{% if item.Rowcount|int >= 10000000 and item.Rowcount|int < 60000000 %}
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    CLUSTERED COLUMNSTORE INDEX
)
;
{% endif %}

{% if item.Rowcount|int >= 60000000 %}
WITH
(
    DISTRIBUTION = HASH([" & "'" & idcolumnname & "'" & "],
    CLUSTERED COLUMNSTORE INDEX
)
;
{% endif %}