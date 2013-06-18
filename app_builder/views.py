from django.http import HttpResponse
from tests import master
from app_builder.analyzer import App, InvalidDict


def test(request):
    ret_code, debug_info = master.main()
    return HttpResponse("%s<br><br>%s" % (ret_code, debug_info))

def validate(request):
    try:
        app_state = request.POST['app_state']
    except KeyError:
        return HttpResponse("Send json string with key 'app_state'", status=400)
    try:
        app_state = simplejson.loads(app_state)
    except Exception:
        return HttpResponse("Not valid json :(", status=400)

    try:
        app = App.create_from_dict(app_state)
    except InvalidDict, e:
        return HttpResponse(str(e))

    return HttpResponse("")
