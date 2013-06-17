#!/usr/bin/python

from app_builder.analyzer import App
from app_builder.analyzer.dict_inited import InvalidDict
import simplejson
import sys

# A decorator that wraps error checking and the right message to be 
# printed on success. This will make code look much cleaner.

def check_exn(msg, *args_e, **kwargs_e):
    def inner_func(func):
        rv = None
        def wrapper(*args, **kwargs):
            try:
                rv = func(*args, **kwargs)
            except:
                raise
            else:
                print msg
                return rv
        return wrapper
    return inner_func

@check_exn("Parsed app state.")
def parse_app_state(app_state_file):
    return simplejson.load(open(app_state_file, 'r'))

@check_exn("Passed analyzer stage")
def create_app(app_state):
    return App.create_from_dict(app_state)

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print >> sys.stdout, "Give the path to a json file"
        sys.exit(1)

    app_state = parse_app_state(args[1])
    app = create_app(app_state)
    


