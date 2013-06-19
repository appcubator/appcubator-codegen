from django.http import HttpResponse
from tests import master
from app_builder.analyzer import App, InvalidDict
import simplejson


def test(request):
    ret_code, debug_info = master.main()
    return HttpResponse("%s<br><br>%s" % (ret_code, debug_info))


def validate(request):
    if request.method == "POST":
        try:
            app_state = request.POST['app_state']
        except KeyError:
            response = HttpResponse("Send json string with key 'app_state'", status=400)
            response['Access-Control-Allow-Origin'] = "*"
            return response
        try:
            app = App.create_from_dict(app_state)
        except InvalidDict, e:
            response = HttpResponse(str(e))
            response['Access-Control-Allow-Origin'] = "*"
            return response
        try:
            app_state = simplejson.loads(app_state)
        except Exception:
            response =  HttpResponse("Not valid json :(", status=400)
            response['Access-Control-Allow-Origin'] = "*"
            return response
        response = HttpResponse(simplejson.dumps(app_state),mimetype='application/json')
        response['Access-Control-Allow-Origin'] = "*"
        return response
    elif request.method == "OPTIONS":
        response = HttpResponse("")
        response['Access-Control-Allow-Origin'] = "*"
        response['Access-Control-Allow-Methods'] = "POST, OPTIONS"
        response['Access-Control-Allow-Headers'] = "X-Requested-With"
        response['Access-Control-Max-Age'] = "180"
        return response
    else:
        response =  HttpResponse("Invalid request", status=400)
        response['Access-Control-Allow-Origin'] = "*"
        return response


    