import unittest
from app_builder.analyzer import App
import random
import os.path
import simplejson

TABLE_NAME_LIST = ["Bottle", "Glass", "Spoon", "Screen", "Monitor", "Cable"]
USER_NAME_LIST = ["Admin", "Carpooler", "Driver", "Wizard", "PG", "VC"]
PRIM_FIELD_LIST = ["Name", "Number Of Kids", "Money In The Bank", "Brew", "Favorite Language", "T-Shirt Size"]
RELATED_NAME_FIELD_TYPES_LIST = ["Socks", "Trousers", "Tweet", "Keyboard"]
URLPART_LIST = ["profile", "barn", "beard", "pool", "notebook", "ryangosling"]

ALIGNMENT_LIST = ["left", "center", "right"]
FIELD_TYPES_LIST = ["number", "text", "image", "date", "email", "file"]
RELATIONAL_FIELD_TYPES_LIST = ["fk", "o2o", "m2m"]


class TestGenerator(object):

    def init_with_blank_state(self):
        module_dir = os.path.dirname(__file__)
        self.state = simplejson.loads(open(os.path.join(module_dir, 'app_states/master_state.json')).read())

    def make_state(self):
        s = self.state

        assert len(s['users']) == 1 and len(s['users'][0]['fields']) > 0, "blank json wasn't what i thought it was"


        return s



class IsComprehensiveTestCase(unittest.TestCase):

    def setUp(self):
        t = TestGenerator()
        t.init_with_blank_state()
        self.d = t.make_state()
        self.app = App.create_from_dict(self.d)

    def test_has_multiple_entities(self):
        pass

    def test_each_entity_has_multiple_primitive_fields_of_all_types(self):
        pass

    def test_each_entity_has_at_least_two_relational_fields(self):
        pass

    def test_all_relational_fields_occur_at_least_twice(self):
        pass

    def test_has_multiple_page(self):
        pass

    def test_have_pages_with_multiple_entities_in_context(self):
        pass

    def test_each_page_has_at_least_two_forms(self):
        pass

    def test_all_entities_have_create_forms(self):
        pass

    def test_some_create_forms_have_no_relations(self):
        pass

    def test_has_relational_create_form_involving_user(self):
        pass

    def test_has_relational_create_form_involving_page(self):
        pass

    def test_have_redirect_and_refresh(self):
        pass

if __name__ == '__main__':
    unittest.main()
