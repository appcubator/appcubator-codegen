{% extends "form_receiver.py" %}
{% set login_function = imports['django.auth.login'] %}
{% set authenticate_function = imports['django.auth.authenticate'] %}
{% set request = locals['request'] %}

{% block declaration %}
@require_POST
def {{ fr.identifier }}({{request}}):
    """Create a User object"""
{% endblock %}

    {% block init_forms %}
    form = {{fr.form_id}}({{request}}.POST)
    {% endblock %}

        {% block do_stuff_with_valid_form %}
        user = form.save()
        new_user = {{authenticate_function}}(username={{request}}.POST['username'],
                                                        password={{request}}.POST['password1'])
        {{login_function}}({{request}}, new_user)
        {% endblock %}
