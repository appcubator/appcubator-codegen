from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import redirect as redirect
from django.db.models import Q
import re

def normalize_query(query_string):
    qterms = re.compile(r'"([^"]+)"|(\S+)').findall
    normalizer = re.compile(r'\s{2,}').sub
    return [ normalizer(' ', (q[0] or q[1]).strip()) for q in qterms(query_string) ]

def get_query(query_string, search_fields):
    qterms = normalize_query(query_string)
    query = None
    for qterm in qterms:
        or_query = None
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: qterm})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query

def get_results(query_string, fields):
	query_obj = get_query(query_string, fields)
	return Entry.objects.filter(query_obj)

def json_response(data={}, errors={}, success=True):
    data.update({
        'errors': errors,
        'success': len(errors) == 0 and success,
    })
    return simplejson.dumps(data)


class JsonResponse(HttpResponse):
    
    def __init__(self, data={}, errors={}, success=True):
        json = json_response(data=data, errors=errors, success=success)
        super(JsonResponse, self).__init__(json, mimetype='application/json')

