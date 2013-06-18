#!/usr/bin/python

from app_builder.analyzer import App
from app_builder.analyzer.dict_inited import InvalidDict
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
from app_builder.tests.app_state_interface import AppStateTestInterface
import simplejson
import fileinput
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
                print >> sys.stderr, "[test_runner] Encountered exception: ", sys.exc_info()[0]
                raise
            else:
                print "[test_runner] %s" % msg
                return rv
        return wrapper
    return inner_func

### Basic test primitives ###
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

@check_exn("Deployed locally.")
def deploy_locally(coder):
    #TODO(nkhadke): fix css
    return write_to_fs(coder)


### Helper functions ###
def basic_deploy(json_file):
    app_state = parse_app_state(json_file)
    app = create_app(app_state)
    codes = create_indiv_components(app)
    coder = create_code(codes)
    fs_loc = deploy_locally(coder)
    get_rid_of_wsgi(fs_loc)
    return fs_loc

def get_rid_of_wsgi(dest):
    for line in fileinput.FileInput(dest + "/settings.py", inplace=True):
        if "WSGI_APPLICATION" in line:
            line = "# " + line.strip()
            print line

def run_generic_tests(apps_interface):
    app_states = apps_interface.get_app_states()
    num_apps = len(app_states)
    for i, app_state in enumerate(app_states):
        print "[test_runner] Running tests for app %s [%d of %d]" %(app_state, (i+1), num_apps)
        dest = basic_deploy(app_state)
        print "[test_runner] Deployed locally at %s" % dest

### Main ###
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        print "[test_runner] Give the path to a json file"
        sys.exit(1)
    apps_interface = AppStateTestInterface()
    run_generic_tests(apps_interface)

