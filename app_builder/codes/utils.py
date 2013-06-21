class RoleRedirectChunk(object):
    def __init__(self, role_codechunk_map):
        "role_codechunk_map maps the role to the code which will evaluate to the URL of the redirect"
        self.role_codechunk_map = role_codechunk_map
    def render(self):
        if len(self.role_codechunk_map) == 0:
            assert False, "wtf, empty map?"
        elif len(self.role_codechunk_map) == 1:
            return str(self.role_codechunk_map.values()[0])

        # if x redirect to y, [elif x redirect to y]*, else assert false structure
        role_codechunk_tuples = self.role_codechunk_map.items()
        accum = ""
        accum += "\nif request.user.get_profile()._role == %s:\n    return JsonResponse(data={'redirect_to': %s})" % role_codechunk_tuples[0]
        for tup in role_codechunk_tuples[1]:
            accum += "\nelif request.user.get_profile()._role == %s:\n    return JsonResponse(data={'redirect_to': %s})" % role_codechunk_tuples[0]
        accum += "\nelse:\n    assert False, 'Role can't have value %r' % request.user.get_profile()._role"
        return accum



class FnCodeChunk(object):
    # wrapper around function which makes the str() method call the function with no args

    def __init__(self, fn):
        self.fn = fn

    def __str__(s):
        return s.fn()

    def __call__(s):
        return s.fn()

    def render(s):
        return str(s)


class AssignStatement(object):
    # a simple helper for x = y statements

    def __init__(self, left_side, right_side):
        self.left_side, self.right_side = (left_side, right_side)

    def __str__(s):
        return s.render()

    def render(self):
        return "%s = %s" % (self.left_side, self.right_side)
        
