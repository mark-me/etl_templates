CREATE TABLE [{{item.Schema}}].[{{item.Code}}]
(
{% for column in item.Columns %}
    {{column.Name}} {{column.DataType}}
    {%- if not loop.last -%}
        ,
    {% endif %}
{% endfor %}

)
WITH
(
    DISTRIBUTION = ROUND_ROBIN,
    CLUSTERED COLUMNSTORE INDEX
)
;