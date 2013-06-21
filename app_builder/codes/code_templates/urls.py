{% set patterns = imports['django.patterns'] %}
{% set url = imports['django.url'] %}
{% set urlpatterns = locals['urlpatterns'] %}

{{urlpatterns}} {% if not urls.first_time %}{{ '+' }}{% endif %}= {{patterns}}('{{ urls.module }}',
    {% for url_string, function in urls.routes %}
    {{url}}({{ url_string }}, '{{ function.identifier }}'),
    {% endfor %}
)

{% if urls.has_social %}
urlpatterns += patterns('', url(r'', include('social_auth.urls')))
{% endif %}
