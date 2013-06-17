#!/usr/bin/python

from app_builder.analyzer import App
from app_builder.analyzer.dict_inited import InvalidDict
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
import simplejson
import sys




def check_exn(msg, exns=[]):
    """
    A decorator that wraps error checking and the right message to be 
    printed on success. This will make code look much cleaner. Takes in
    a message to printed on success and a list of exns to catch.
    """
    exn_tup = tuple(exns)
    def inner_func(func):
        rv = None
        def wrapper(*args, **kwargs):
            try:
                rv = func(*args, **kwargs)
            except exn_tup:
                print >> sys.stderr, "Encountered exception: ", sys.exc_info()[0]
                raise
            else:
                print msg
                return rv
        return wrapper
    return inner_func

@check_exn("Created individual components")
def create_indiv_components(app):
    return create_codes(app)

@check_exn("Combined codes.")
def create_code(codes):
    return Coder.create_from_codes(codes)

@check_exn("Parsed app state.")
def parse_app_state(app_state_file):
    return simplejson.load(open(app_state_file, 'r'))

@check_exn("Passed analyzer stage",exns=[InvalidDict])
def create_app(app_state):
    return App.create_from_dict(app_state)

if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print >> sys.stdout, "Give the path to a json file"
        sys.exit(1)

    app_state = parse_app_state(args[1])
    app = create_app(app_state)
    codes = create_indiv_components(app)
    coder = create_code(codes)

