import time
import re
import unittest
from app_builder.tests.utils import SplinterTestCase
import simplejson

class TestUserRoles(SplinterTestCase):

    json_file_name = re.sub(r'_splinter\.pyc?', '.json', __file__)
    with open(json_file_name) as f:
        APP_STATE = simplejson.load(f)


    def test_nothing(self):
        self.browser.visit(self.url('/'))
        #raw_input()
        self.assertFalse(True)
