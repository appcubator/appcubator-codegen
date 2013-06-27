{% set request = locals['request'] %}
{% set page_context = locals['page_context'] %}
{% set entity = locals['entity'] %}

{% if view.has_search %}
@require_GET
def {{view.identifer}}(request):
    {{page_context}} = {}

    query_string = {{request}}.GET['query']
    field = request.GET['field']
    {{page_context}}['results'] = get_results(query_string, {{entity}}, [field])

    return render({{request}}, "{{ view.template_code_path }}", {{page_context}})
{% endif %}
