class RoleRedirectChunk(object):
    def __init__(self, role_codechunk_tuples, role_field_id):
        "role_codechunk_tuples maps the role to the code which will evaluate to the URL of the redirect"
        self.role_codechunk_tuples = role_codechunk_tuples
        self.role_field_id = role_field_id

    def render(self, ajax=True):
        if len(self.role_codechunk_tuples) == 0:
            assert False, "wtf, empty map?"

        if ajax:
            code_for_redirect = lambda x: "JsonResponse(data={'redirect_to': %s})" % x
        else:
            code_for_redirect = lambda x: "redirect(%s)" % x

        if len(self.role_codechunk_tuples) == 1:
            return "return %s" % code_for_redirect(self.role_codechunk_tuples[0][1])

        # if x redirect to y, [elif x redirect to y]*, else assert false structure
        accum = ""
        accum += "\nif request.user.get_profile().%s == '%s':\n    return %s" % (self.role_field_id, self.role_codechunk_tuples[0][0], code_for_redirect(self.role_codechunk_tuples[0][1]))
        for tup in self.role_codechunk_tuples[1:]:
            accum += "\nelif request.user.get_profile().%s == '%s':\n    return %s" % (self.role_field_id, tup[0], code_for_redirect(tup[1]))
        accum += "\nelse:\n    assert False, 'Role can\\'t have value %r' % request.user.get_profile()." + str(self.role_field_id,) # inconvenient to use a format string here
        return accum


class FnCodeChunk(object):
    # wrapper around function which makes the str() method call the function with no args

    def __init__(self, fn):
        self.fn = fn

    def __str__(s):
        return s.fn()

    def __call__(s):
        return s.fn()

    def render(s, **kwargs):
        return str(s)


class AssignStatement(object):
    # a simple helper for x = y statements

    def __init__(self, left_side, right_side):
        self.left_side, self.right_side = (left_side, right_side)

    def __str__(s):
        return s.render()

    def render(self):
        return "%s = %s" % (self.left_side, self.right_side)
        
