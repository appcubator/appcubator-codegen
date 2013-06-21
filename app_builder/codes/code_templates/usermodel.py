{% extends "model.py" %}

{% set models = imports['django.models'] %}
{% set User = imports['django.models.User'] %}
{% set user = locals['user o2o'] %}

{% block class_name %}{{model.user_profile_identifier}}{% endblock %}

    {% block fields %}
{{ super() }}
    {{user}} = {{models}}.OneToOneField({{User}}, blank=True, null=True) # Application code will ensure this is not null.
    {% endblock %}


    {% block instancemethods %}
    {% if not model.is_user_model is undefined and model.is_user_model%}
    @staticmethod
    def userprofile_post_save_hook(sender, instance, created, **kwargs):
        try:
            instance.get_profile()
        except {{model.user_profile_identifier}}.DoesNotExist:
            {{model.user_profile_identifier}}({{user}}=instance).save()
    {% endif %}
    {% endblock %}


{% block signals %}
{% if not model.is_user_model is undefined and model.is_user_model%}
{{post_save}}.connect({{model.user_profile_identifier}}.userprofile_post_save_hook, sender=User)
{% endif %}
{% endblock %}
