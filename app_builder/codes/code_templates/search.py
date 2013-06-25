{% set request = locals['request'] %}
{% set page_context = locals['page_context'] %}

{% if view.has_search %}
@require_GET
def search(request):
    {{page_context}} = {}

    query_string = {{request}}.GET['query']
    field = request.GET['field']
    model_name = request.GET['model']
    {{page_context}}['results'] = get_results(query_string, model_name, [field])

    return render({{request}}, "{{ view.template_code_path }}", {{page_context}})
{% endif %}
