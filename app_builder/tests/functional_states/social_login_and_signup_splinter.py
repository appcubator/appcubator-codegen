from splinter import Browser
import time
import unittest
from app_builder.tests.utils import SplinterTestCase

class TestSup(SplinterTestCase):

    APP_DIR = APP_DIR # binds APP_DIR, a variable injected into the namespace by testrunner, to the class,
                      # so that SplinterTestCase knows how to start the server

    def test_signup_button_creates_and_redirects_based_on_role(self):
        pass
    def test_signup_twice_not_allowed(self):
        pass
    def test_login_and_logout_after_signup_works_properly(self):
        pass
    def test_no_login_before_signing_up(self):
        pass


def main():
    """
    Multi user social auth test.
    """
    with Browser() as browser:
        prefix = "http://127.0.0.1:8000"
        url = lambda x: prefix + str(x)
        route = lambda x: x.replace(prefix, "")


        ### Ignore below, it's just sample code.


        def test_logged_out():
            # try to go to restricted page, get redirected to home.
            browser.visit(url('/restricted'))
            assert route(browser.url) != '/restricted/', "Access control didn't prevent me from visiting restricted page."
            # i'm ignoring the ?next for now tho.
            assert route(browser.url) == '/?next=/restricted/', "Not logged in, bounced to %r instead of homepage" % route(browser.url)


        # try to signup, expect to be redirected to restricted.
        browser.visit(url('/'))
        signup_form = browser.find_by_tag('form')[1]
        signup_form.find_by_name('username').fill('karan')
        signup_form.find_by_name('password1').fill('123')
        signup_form.find_by_name('password2').fill('123')
        signup_form.find_by_name('email').fill('k@k.com')
        signup_form.find_by_css('input.btn').click()

        if browser.is_text_present('error'):
            assert False, "Looks like there was an error siging up."
        for e in browser.find_by_css('.form-error'):
            assert e.value.strip() == '', "Found an error while signing up: %r" % e.value

        assert route(browser.url) == '/restricted/'

        # try to logout, access restricted, then login, access restricted
        browser.find_by_id('logout')[0].click()
        assert route(browser.url) == '/'
        test_logged_out()

        login_form = browser.find_by_tag('form')[0]
        login_form.find_by_name('username').fill('karan')
        login_form.find_by_name('password').fill('123')
        login_form.find_by_css('input.btn').click()
        time.sleep(1)
        assert route(browser.url) == '/restricted/', "Did not redirect to restricted. Ended up at %r" % route(browser.url)



if __name__ == "__main__":
    #main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSup)
    unittest.TextTestRunner(verbosity=2).run(suite)
    #unittest.main(argv=('test',))
