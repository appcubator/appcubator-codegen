{% set request = locals['request'] %}
{% set page_context = locals['page_context'] %}
{% set entity = locals['entity'] %}

{% if view.has_search %}
def {{view.identifier}}({{request}}, page_context):
    if 'query' not in {{request}}.GET:
	    return
    query_string = {{request}}.GET['query']
    field = request.GET['field']
    {{page_context}}['results'] = get_results(query_string, "{{entity}}", [field])
{% endif %}
