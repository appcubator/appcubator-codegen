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

