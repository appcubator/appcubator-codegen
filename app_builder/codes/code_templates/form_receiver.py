
{% set JsonResponse = imports['django.JsonResponse'] %}
{% set simplejson = imports['django.simplejson'] %}
{% set reverse = imports['django.url.reverse'] %}
{% set request = locals['request'] %}
{% set page_view_id = locals['page_view_id']() %}
{% set redirect_url = locals['redirect_url'] %}

@require_POST
def {{ fr.identifier }}({{request}}{% block args %}{% endblock %}):
    {% block init_forms %}
    form = {{ fr.form_id }}({{request}}.POST)
    {% endblock %}
    if form.is_valid():
        {% block do_stuff_with_valid_form %}
        obj = form.save()
        {% endblock %}
        {{redirect_url}} = {{reverse}}('{{ page_view_id }}')
        return {{JsonResponse}}(data={'redirect_to':redirect_url})

    return {{JsonResponse}}(errors=form.errors)

