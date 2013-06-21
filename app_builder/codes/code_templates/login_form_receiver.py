{% extends "form_receiver.py" %}
{% set login_function = imports['django.auth.login'] %}
{% set request = locals['request'] %}

{% block declaration %}
@require_POST
def {{ fr.identifier }}({{request}}):
    """
    Handles the login action.
    """
{% endblock %}
    {#redirect_to = "{{ form_receiver.goto_view.view_path() }}"#}

    {% block init_forms %}
    form = {{ fr.form_id }}(None, data={{request}}.POST)
    {% endblock %}

        {% block do_stuff_with_valid_form %}
        {{login_function}}({{request}}, form.get_user())
        {% endblock %}

        {% block redirect %}
        {% if not (fr.role_redirect is undefined) %}
        {{ fr.role_redirect.render()|indent(8) }}
        {% else %}
{{ super() }}
        {% endif %}
        {% endblock %}
