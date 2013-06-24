from splinter import Browser

with Browser() as browser:
    # Visit URL
    url = "http://127.0.0.1:8000/"
    browser.visit(url)
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
    assert browser.url == 'http://127.0.0.1:8000/'
