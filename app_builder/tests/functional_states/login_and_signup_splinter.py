from splinter import Browser

def main():
    with Browser() as browser:
        prefix = "http://127.0.0.1:8000"
        url = lambda x: prefix + str(x)
        route = lambda x: x.replace(prefix, "")

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

if __name__ == "__main__":
    main()
