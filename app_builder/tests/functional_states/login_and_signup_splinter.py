import time
import unittest
from app_builder.tests.utils import SplinterTestCase

class TestLoginSignup(SplinterTestCase):

    APP_DIR = APP_DIR # binds APP_DIR, a variable injected into the namespace by testrunner, to the class,
                      # so that SplinterTestCase knows how to start the server
    try:
        PORT = PORT
    except NameError, e:
        print "E: %s" % e 
        PORT = 8000

    def setUp(self):
        super(TestLoginSignup, self).setUp()
        self.browser.visit(self.url('/'))

    def assert_logged_out(self):
        # assumes protected pages are working
        # try to go to restricted page, get redirected to home.
        self.browser.visit(self.url('/restricted'))
        self.assertNotEqual(self.route(self.browser.url), '/restricted/', "Access control didn't prevent me from visiting restricted page.")
        # i'm ignoring the ?next for now tho on the backend
        assert self.route(self.browser.url) == '/?next=/restricted/', "Not logged in, bounced to %r instead of homepage" % self.route(self.browser.url)

    def assert_logged_in(self):
        # assumes protected pages are working
        self.browser.visit(self.url('/restricted'))
        self.assertEqual(self.route(self.browser.url), '/restricted/', msg="Did not redirect to restricted. Ended up at %r" % self.route(self.browser.url))

    def signup(self):
        self.browser.visit(self.url('/'))
        signup_form = self.browser.find_by_tag('form')[1]
        signup_form.find_by_name('username').fill('karan')
        signup_form.find_by_name('password1').fill('123')
        signup_form.find_by_name('password2').fill('123')
        signup_form.find_by_name('email').fill('k@k.com')
        signup_form.find_by_css('input.btn').click()

    def login(self):
        self.browser.visit(self.url('/'))
        login_form = self.browser.find_by_tag('form')[0]
        login_form.find_by_name('username').fill('karan')
        login_form.find_by_name('password').fill('123')
        login_form.find_by_css('input.btn').click()

    def logout(self):
        self.browser.find_by_id('logout')[0].click()

    def test_signup_redirect(self):
        # try to signup, expect to be redirected to restricted.
        self.signup()
        self.assertFalse(self.browser.is_text_present('error'), msg="Looks like there was an error siging up.")
        for e in self.browser.find_by_css('.form-error'):
            self.assertEqual(e.value.strip(), '', msg="Found an error while signing up: %r" % e.value)

        self.assert_logged_in()

    def test_logout_works(self):
        self.signup()
        self.login()
        time.sleep(.5)
        self.logout()
        self.assertEqual(self.route(self.browser.url), '/')
        self.assert_logged_out()

    def test_login_works(self):
        self.signup()
        self.login()
        self.assert_logged_in()


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLoginSignup)
    unittest.TextTestRunner(verbosity=2).run(suite)
