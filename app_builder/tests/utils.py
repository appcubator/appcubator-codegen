import os, os.path
import unittest
from app_builder.analyzer.analyzer import App
from splinter import Browser
from app_builder.app_manager import AppManager

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
            print "Trying to connect to server"
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
        port = self.__class__.PORT
        hostname = "testing.appcubator.com"
        url = "http://%s:%d/" % (hostname, port)

        # start the server
        am = AppManager(self.__class__.APP_DIR, venv_dir=os.environ['APP_VENV'], settings_module='settings.dev')
        self.p = am.Popen("python manage.py runserver %d" % port)
        self._app_manager = am

        # wait until server is ready
        ping_until_success(url)

        self.browser = Browser()
        self.prefix = url[:-1] # without the ending fwd slash
        self.url = lambda x: self.prefix + str(x)
        self.route = lambda x: x.replace(self.prefix, "")


    def tearDown(self):
        self.browser.quit()

        # send sigterm to all processes in the group
        os.killpg(self.p.pid, signal.SIGTERM)
        self.p.wait()
        self._app_manager.run_command("python manage.py flush")

