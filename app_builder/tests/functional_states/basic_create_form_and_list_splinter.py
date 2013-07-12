import time
import os
import unittest
from app_builder.tests.utils import SplinterTestCase

class TestCreateSimpleList(SplinterTestCase):

    APP_DIR = APP_DIR # binds APP_DIR, a variable injected into the namespace by testrunner, to the class,
                      # so that SplinterTestCase knows how to start the server

    try:
        PORT = PORT
    except NameError, e:
        print "E: %s" % e
        PORT = 8000

    def setUp(self):
        super(TestCreateSimpleList, self).setUp()
        self.browser.visit(self.url('/'))

    def login_to_facebook(self):
        assert 'facebook.com' in self.browser.url
        email_input = self.browser.find_by_id('email')[0]
        email_input.fill(os.environ['FB_USERNAME'])
        passwd_input = self.browser.find_by_id('pass')[0]
        passwd_input.fill(os.environ['FB_PASSWD'])
        self.browser.find_by_name('login')[0].click()

    def tweet(self, s):
        self.browser.visit(self.url('/Tweet_Feed/'))
        text_field = self.browser.find_by_css('input[type="text"]')[0]
        submit_field = self.browser.find_by_css('input[type="submit"]')[0]
        text_field.fill(s)
        submit_field.click()

    def test_create(self):
        self.browser.find_by_css('.facebook-login-btn')[0].click()
        self.login_to_facebook()
        self.tweet('abcdefghijklmnopqrstuvwxyz')
        self.browser.visit(self.url('/Tweet_Feed/'))
        self.assertTrue(self.browser.is_text_present('abcdefghijklmnopqrstuvwxyz'))

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCreateSimpleList)
    unittest.TextTestRunner(verbosity=2).run(suite)
