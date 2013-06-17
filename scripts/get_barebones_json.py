#!/usr/bin/python

"""
Validates JSON as valid app state, then returns the stripped version (only the stuff backend cares about, defined in the _schemas.
"""


from app_builder.analyzer import App
from app_builder.analyzer.dict_inited import InvalidDict
import simplejson
import sys
import pprint

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print >> sys.stdout, "Give the path to a json file"
        sys.exit(1)

    app_state = simplejson.load(open(args[1], 'r'))

    try:
        app = App.create_from_dict(app_state)
    except InvalidDict:
        raise
    else:
        print >> sys.stdout, "Passed analyzer stage"

    stripped_dict = App._recursively_create(app_state, {
                                "_type": App}, data_only=True)  # helper function needed for schema based recursion
    json = simplejson.dumps(stripped_dict, indent=2)
    print >> sys.stdout, json


