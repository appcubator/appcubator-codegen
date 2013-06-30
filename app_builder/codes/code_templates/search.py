{% set request = locals['request'] %}
{% set page_context = locals['page_context'] %}
{% set model_id = locals['model_id'] %}
{% set results = locals['results'] %}
{% set simplejson = imports['django.simplejson'] %}

{% if view.has_search %}
def {{view.identifier}}({{request}}, page_context):
    if 'query' not in {{request}}.GET:
	    return
    query_string = {{request}}.GET['query']
    import HTMLParser
    h = HTMLParser.HTMLParser()
    unescaped_field_json = h.unescape(request.GET['field_json'])
    field_names = {{simplejson}}.loads(unescaped_field_json)
    {{page_context}}['{{results}}'] = get_results(query_string, "{{model_id}}", field_names)
{% endif %}
