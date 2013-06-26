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
        {{ fr.role_redirect.render()|indent(8) }}
    elif action == 'signup':
        if userprofile.role is not None:
            return # already signed up
        role = request.GET['role']
        userprofile.role = role
        userprofile.save()
        {{ signup_role_redirect.render()|indent(8) }}
    else:
        assert False
