{% set models = imports['django.models'] %}
{% set post_save = imports['django.signals.post_save'] %}

class {% block class_name %}{{model.identifier}}{% endblock %}({{models}}.Model):
    {% block fields %}
    {% for f in model.fields %}
    {{ f.identifier }} = {{models}}.{{ f.django_type }}({% for a in f.args %}{{ a }}, {% endfor %}{% for k,v in f.kwargs().items() %}{{ k }}={{ v }}{% if not loop.last %}, {% endif %}{% endfor %})
    {% endfor %}
    {% endblock %}

    {% block instancemethods %}
    {% endblock %}

{% block signals %}
{% endblock %}

