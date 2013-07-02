{% set forms = imports['django.forms'] %}

class {% block class_name %}{{ form.identifier }}{% endblock %}({{forms}}.ModelForm):

    class Meta:
        model = {{ form.model_id }}
        fields = ({{ form.included_field_string }})
