#!/usr/bin/python

from app_builder.analyzer import App, InvalidDict
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
from app_builder.tests.app_state_interface import AppStateTestInterface


import os
import signal
import sys
import shlex
import subprocess
import simplejson
import fileinput
import traceback
import logging
import argparse
import requests
import time


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


DEFAULT_STATE_PATH = os.path.join(os.path.dirname(__file__), '..', 'app_builder', 'tests', 'app_states')


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

def run_django_tests(dest):
    cmd = "python scripts/test.py"
    child_env = os.environ.copy()
    child_env['PYTHONPATH'] = dest
    p = subprocess.Popen(shlex.split(cmd), cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=child_env)
    out, err = p.communicate()
    if p.returncode != 0:
        logger.error("Testing failed! Output: %s\n%s" % (out, err))
    else:
        logger.info("These tests passed!!! Much swag.")
    logger.debug("Test output: %s\n%s" % (out, err))


def get_rid_of_wsgi(dest):
    # don't get rid of the print statement. it's magical
    for line in fileinput.FileInput(dest + "/settings.py", inplace=True):
        if "WSGI_APPLICATION" in line:
            line = "# " + line.rstrip()
        print line.rstrip()


def run_acceptance_tests(splinter_file):
    "Executes the splinter file to run the acceptance tests."
    execfile(splinter_file, {}, {})


def ping_until_success(url, retries=10):
    "Holds up this process until a 200 is received from the server."
    tries = 0
    successful = False
    while not successful and tries < retries:
        try:
            r = requests.get(url)
        except requests.exceptions.ConnectionError:
            pass
        else:
            successful = r.status_code == 200
        tries += 1
        time.sleep(1)
    if tries == retries:
        raise Exception("Tried to ping until 200, but just couldn't get that dough brah.")
    return


def run_generic_tests(app_state_dir, specific_state_names=None):
    if specific_state_names is None:
        fnames_to_test = [ fname for fname in os.listdir(app_state_dir)  if fname.endswith('.json') ]
    else:
        fnames_to_test = [ fname for fname in os.listdir(app_state_dir) if fname.endswith('.json') and fname[:-5] in specific_state_names ]

    num_apps = len(fnames_to_test)
    for i, json_file_name in enumerate(fnames_to_test):
        json_file = os.path.join(app_state_dir, json_file_name)
        logger.info("Running tests for app %s [%d of %d]" %(json_file, (i+1), num_apps))
        try:
            dest = basic_deploy(json_file)
        except:
            logger.error("App %s failed to deploy" % json_file)
            logger.error("Encountered exception: ", sys.exc_info()[0])
            continue
        else:
            logger.info("App %s Deployed locally at %s" % (json_file_name, dest))
            syncdb(dest)
            run_django_tests(dest)
            splinter_file = os.path.join(app_state_dir, '%s_splinter.py' % json_file_name.replace('.json',''))
            if os.path.isfile(splinter_file):
                # start the server
                cmd = "python manage.py runserver"
                p = subprocess.Popen(shlex.split(cmd), cwd=dest, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setpgrp)
                try:
                    # wait until server is ready
                    ping_until_success('http://127.0.0.1:8000/')
                    run_acceptance_tests(splinter_file)
                finally:
                    # send sigterm to all processes in the group
                    os.killpg(p.pid, signal.SIGTERM)
                    print "waiting"
                    p.wait()
                    print "process with pid %d should be dead now." % p.pid
            else:
                logger.warn("No splinter file found for %s" % json_file_name)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Deploy and test some JSONs.')

    parser.add_argument('--path', help='the path at which you can find the json', dest='app_state_path', default=DEFAULT_STATE_PATH)
    parser.add_argument('app_state_names', metavar='json', nargs='*', help='the name of the json file, without the json ext')

    args = parser.parse_args()

    if len(args.app_state_names) == 0:
        run_generic_tests(args.app_state_path)
    else:
        run_generic_tests(args.app_state_path, specific_state_names=args.app_state_names)

