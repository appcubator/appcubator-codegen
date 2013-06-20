#!/usr/bin/python

from app_builder.analyzer import App, InvalidDict
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
from app_builder.tests.app_state_interface import AppStateTestInterface


import os
import sys
import shlex
import subprocess
import simplejson
import fileinput
import traceback
import logging


# configure loggers
from app_builder.analyzer import logger as analyzer_logger
from app_builder.coder import logger as coder_logger
from app_builder.controller import logger as controller_logger

analyzer_logger.setLevel('ERROR')
coder_logger.setLevel('ERROR')
controller_logger.setLevel('ERROR')

logger = logging.getLogger('scripts.test_runner')
logger.setLevel('INFO')
logger.addHandler(logging.StreamHandler())


def check_exn(msg):
    """
    A decorator that wraps error checking and the right message to be
    printed on success. This will make code look much cleaner. Takes in
    a message to printed on success.
    """
    def inner_func(func):
        def wrapper(*args, **kwargs):
            try:
                rv = func(*args, **kwargs)
            except Exception:
                logger.error(traceback.format_exc())
                raise
            else:
                logger.info(msg)
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

@check_exn("Passed analyzer stage")
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

def syncdb(dest):
    cmd = "python scripts/syncdb.py"
    child_env = os.environ.copy()
    child_env['PYTHONPATH'] = dest
    p = subprocess.Popen(shlex.split(cmd), cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env)
    out, err = p.communicate()
    logger.debug("Syncdb output: %s\n%s" % (out, err))

def run_tests(dest):
    cmd = "python scripts/test.py"
    child_env = os.environ.copy()
    child_env['PYTHONPATH'] = dest
    p = subprocess.Popen(shlex.split(cmd), cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env)
    out, err = p.communicate()
    if p.returncode != 0:
        logger.error("Testing failed! Output: %s\n%s" % (out, err))
    logger.debug("Test output: %s\n%s" % (out, err))


def get_rid_of_wsgi(dest):
    # don't get rid of the print statement. it's magical
    for line in fileinput.FileInput(dest + "/settings.py", inplace=True):
        if "WSGI_APPLICATION" in line:
            line = "# " + line.rstrip()
        print line.rstrip()

def run_generic_tests(apps_interface):
    app_states = apps_interface.get_app_states()
    num_apps = len(app_states)
    for i, app_state in enumerate(app_states):
        logger.info("Running tests for app %s [%d of %d]" %(app_state, (i+1), num_apps))
        try:
            dest = basic_deploy(app_state)
        except:
            logger.error("FAIL: App %s failed." % app_state)
            logger.error("Encountered exception: ", sys.exc_info()[0])
        else:
            logger.info("PASS: App %s Deployed locally at %s" % (app_state.replace('.json', ''), dest))
            syncdb(dest)
            run_tests(dest)

### Main ###
if __name__ == "__main__":
    args = sys.argv
    if len(args) == 1:
        apps_interface = AppStateTestInterface()
        logger.info("Using default app_states directory.")
    elif len(args) == 2:
        apps_interface = AppStateTestInterface(app_state_dir=args[1].rstrip())
    else:
        print >> sys.stderr, "Usage: python -m scripts.test_runner [path to app states]"
        sys.exit(1)

    run_generic_tests(apps_interface)

