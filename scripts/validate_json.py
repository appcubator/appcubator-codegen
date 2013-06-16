#!/usr/bin/python

from app_builder.analyzer import App
from app_builder.analyzer.dict_inited import InvalidDict
import simplejson
import sys

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

