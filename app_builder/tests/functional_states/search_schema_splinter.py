import time
import unittest
from app_builder.tests.utils import SplinterTestCase

class TestSearch(SplinterTestCase):

    APP_DIR = APP_DIR # binds APP_DIR, a variable injected into the namespace by testrunner, to the class,
                      # so that SplinterTestCase knows how to start the server

    try:
        PORT = PORT
    except NameError, e:
        print "E: %s" % e
        PORT = 8000

    def setUp(self):
        super(TestSearch, self).setUp()
        self.browser.visit(self.url('/'))

    def test_nothing(self):
        raw_input()

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSearch)
    unittest.TextTestRunner(verbosity=2).run(suite)
