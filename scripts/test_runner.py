#!/usr/bin/python

from app_builder.analyzer import App, InvalidDict
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
from app_builder.tests.app_state_interface import AppStateTestInterface
from app_builder.app_manager import AppManager


import os, os.path
import signal
import sys
import shlex
import simplejson
import fileinput
import traceback
import logging
import argparse
import requests
import time
from multiprocessing import Process


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


DEFAULT_STATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'app_builder', 'tests', 'functional_states')
VENV_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'appcubator-deploy', 'child_venv')


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
    app = App.create_from_dict(app_state)
    return app

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
    am = AppManager(dest, venv_dir=VENV_DIR, settings_module='settings.dev')
    ret, out, err = am.run_command("python scripts/syncdb.py")
    logger.debug("Syncdb output: %s\n%s" % (out, err))

def run_django_tests(dest):
    am = AppManager(dest, venv_dir=VENV_DIR, settings_module='settings.dev')
    ret, out, err = am.run_command("python manage.py test webapp")
    if ret != 0:
        logger.error("Testing failed! Output: %s\n%s" % (out, err))
    else:
        logger.info("These tests passed!!! Much swag.")
    logger.debug("Test output: %s\n%s" % (out, err))


def get_rid_of_wsgi(dest):
    # don't get rid of the print statement. it's magical
    for line in fileinput.FileInput(dest + "/settings/common.py", inplace=True):
        if "WSGI_APPLICATION" in line:
            line = "# " + line.rstrip()
        print line.rstrip()


def run_tests_for_json_file(json_file, port=8000):
    json_file_name = os.path.basename(json_file)
    try:
        dest = basic_deploy(json_file)
    except:
        logger.error("App %s failed to deploy" % json_file)
        logger.error("Encountered exception: ", sys.exc_info()[0])
        return

    logger.info("App %s Deployed locally at %s" % (json_file_name, dest))
    syncdb(dest) # this may not be necessary since we're using testserver instead of runserver.
    run_django_tests(dest)
    splinter_file = os.path.join('%s_splinter.py' % json_file.replace('.json',''))
    if os.path.isfile(splinter_file):
        execfile(splinter_file, {"__name__": "__main__", "APP_DIR": dest, "VENV_DIR": VENV_DIR, "PORT": port}) # this runs the main test file, which is unittest driven
    else:
        logger.warn("No splinter file found for %s" % json_file_name)


def run_tests_in_dir(app_state_dir, specific_state_names=None, parallel=False):
    if specific_state_names is None:
        fnames_to_test = [ fname for fname in os.listdir(app_state_dir)  if fname.endswith('.json') ]
    else:
        fnames_to_test = [ fname for fname in os.listdir(app_state_dir) if fname.endswith('.json') and fname[:-5] in specific_state_names ]

    num_apps = len(fnames_to_test)
    processes = []
    port = 8001

    for i, json_file_name in enumerate(fnames_to_test):
        def test_f(port,
                json_file_name=json_file_name, app_state_dir=app_state_dir, i=i, num_apps=num_apps, logger=logger):
            logger.info("Running tests for app %s [%d of %d]" %(json_file_name, (i+1), num_apps))
            json_file = os.path.join(app_state_dir, json_file_name)
            logger.info("Json file at %s" % json_file)
            run_tests_for_json_file(json_file, port=port)

        if parallel:
            p = Process(target=test_f, args=(port,))
            port += 1
            p.start()
            processes.append(p)
        else:
            test_f(port)
            port += 1

    if parallel:
        for p in processes:
            p.join()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Deploy and test some JSONs.')

    parser.add_argument('--path', help='the path at which you can find the json', dest='app_state_path', default=DEFAULT_STATE_PATH)
    parser.add_argument('app_state_names', metavar='json', nargs='*', help='the name of the json file, without the json ext')

    args = parser.parse_args()

    if len(args.app_state_names) == 0:
        run_tests_in_dir(args.app_state_path)
    else:
        run_tests_in_dir(args.app_state_path, specific_state_names=args.app_state_names)

