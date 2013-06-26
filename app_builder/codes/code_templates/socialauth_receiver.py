{% set JsonResponse = imports['django.JsonResponse'] %}
{% set simplejson = imports['django.simplejson'] %}
{% set reverse = imports['django.url.reverse'] %}
{% set request = locals['request'] %}
{% if fr.redirect %}
{% set redirect_url_code = locals['redirect_url_code']() %}
{% set redirect_url = locals['redirect_url'] %}{# this is just the variable placeholder to avoid name collisions. not actual url. #}
{% endif %}

def {{ fr.identifier }}({{request}}):
    userprofile = request.user.get_profile()
    action = request.GET['action']
    if action == 'login':
        if userprofile.role is not None:
            return # haven't yet signed up
        # put role-based redirect here.
    elif action == 'signup':
        if userprofile.role is not None:
            return # already signed up
        role = request.GET['role']
        userprofile.role = role
        userprofile.save()
        {% if fr.redirect %}
        {{redirect_url}} = {{redirect_url_code}}
        return {{JsonResponse}}(data={'redirect_to':{{redirect_url}}})
        {% else %}
        return {{JsonResponse}}(data={'refresh':True})
        {% endif %}
    else:
        assert False
