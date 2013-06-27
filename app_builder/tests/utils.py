import os, os.path
import unittest
from app_builder.analyzer.analyzer import App

MASTER_APP_STATE = os.path.join(os.path.dirname(__file__), "app_states", "master_state.json")

class BaseStateTestCase(unittest.TestCase):
    def setUp(self):
        self.app_state = simplejson.load(open(MASTER_APP_STATE, 'r'))
        self.alter_base_state(self)
        self.app = App.create_from_dict(self.app_state)

    def alter_base_state(self):
        "Override this method to alter self.app_state before it gets parsed into an App object."
        pass


import requests, time

def ping_until_success(url, retries=8):
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


import signal, subprocess, shlex
class SplinterTestCase(unittest.TestCase):
    def setUp(self):
        # start the server
        cmd = "python manage.py testserver"
        self.p = subprocess.Popen(shlex.split(cmd), cwd=self.__class__.APP_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, preexec_fn=os.setpgrp)
        # wait until server is ready
        ping_until_success('http://127.0.0.1:8000/')
    def tearDown(self):
        # send sigterm to all processes in the group
        os.killpg(self.p.pid, signal.SIGTERM)
        self.p.wait()

