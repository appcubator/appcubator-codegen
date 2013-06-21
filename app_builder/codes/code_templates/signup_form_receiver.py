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
        {% if not fr.signup_role is undefined %}
        userprofile = user.get_profile()
        userprofile.{{fr.locals['role_field_id']}} = '{{fr.signup_role}}'
        userprofile.save()
        {% endif %}
        new_user = {{authenticate_function}}(username={{request}}.POST['username'],
                                                        password={{request}}.POST['password1'])
        {{login_function}}({{request}}, new_user)
        {% endblock %}
