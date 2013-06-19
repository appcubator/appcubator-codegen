from django.http import HttpResponse
from tests import master
from django.views.decorators.csrf import csrf_exempt
from app_builder.analyzer import App, InvalidDict
import simplejson


def test(request):
    ret_code, debug_info = master.main()
    return HttpResponse("%s<br><br>%s" % (ret_code, debug_info))


@csrf_exempt
def validate(request):
    app_state = request.POST['app_state']
    try:
        app_state = simplejson.loads(app_state)
    except Exception:
        return HttpResponse("Not valid json :(", status=400)

    try:
        app = App.create_from_dict(app_state)
    except InvalidDict, e:
        return HttpResponse(str(e))

    return HttpResponse("")

