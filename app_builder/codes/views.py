from app_builder import naming
from utils import FnCodeChunk, RoleRedirectChunk
from . import env

class SocialAuthHandler(object):

    def __init__(self, identifier):
        self.identifier = identifier
        self.namespace = naming.Namespace(parent_namespace=identifier.ns)
        self.code_path = 'webapp/form_receivers.py'
        self.locals = {"request": self.namespace.new_identifier('request')}
        self.redirect = False
        self.signup_role_redirect_map = {}

    def add_role_redirect(self, role_redirect):
        assert not hasattr(self, 'role_redirect'), "There were multiple login with facebook buttons in the app. Butwai."
        self.role_redirect = role_redirect

    def add_signup_role_redirect(self, signup_role_id, redirect_to, role_field_id=None):
        """OK for role_field_id to be None in the single user case."""
        assert signup_role_id not in self.signup_role_redirect_map, "There were multiple signup buttons with the same signupRole. Butwai."
        self.signup_role_redirect_map[signup_role_id] = redirect_to
        self._update_signup_redirect_chunk(role_field_id)

    def _update_signup_redirect_chunk(self, role_field_id):
        assert len(self.signup_role_redirect_map) > 0, "Only update it if there is some role mapping!"
        if len(self.signup_role_redirect_map) == 1:
            rr = FnCodeChunk(lambda: "redirect(%s)" % self.signup_role_redirect_map.values[0].to_code(template=False))
        else:
            role_linklang_tuples = []
            for role_id, redirect_to in self.signup_role_redirect_map.items():
                fn = FnCodeChunk(lambda redirect_to=redirect_to: redirect_to.to_code(template=False))
                role_linklang_tuples.append((role_id, fn))
            rr = RoleRedirectChunk(role_linklang_tuples, role_field_id)
        self.signup_role_redirect = rr

    def render(self):

        return env.get_template("socialauth_receiver.py").render(fr=self, locals=self.locals, imports=self.namespace.imports())


class DjangoPageSearch(object):
    def __init__(self, identifier, template_code_path="search.html", access='all', search=True):
        """
        Takes the last page and adds search to all pages by referencing the views/pages.py file.
        """
        self.identifier = "search_%s" % identifier.__str__().lower()
        self.has_search = search
        self.code_path = "webapp/pages.py"

        self.locals = {}
        self.namespace = naming.Namespace()
        self.locals['request'] = self.namespace.new_identifier('request', ref="VIEW.REQUEST")
        self.locals['page_context'] = self.namespace.new_identifier('page_context')
        self.locals['entity'] = identifier.__str__()

        # access level
        self.login_required = False
        if access == 'users':
            self.login_required = True

        self.template_code_path = template_code_path

    def render(self):
        return env.get_template('search.py').render(view=self, locals=self.locals)


class DjangoPageView(object):

    def __init__(self, identifier, args=None, template_code_path="", queries=None, access='all', search=False):
        """
        args is a list of tuples: (identifier, some_data_as_dict)
        """
        self.identifier = identifier
        self.has_search = search
        self.code_path = "webapp/pages.py"

        self.locals = {}
        # args, make a namespace for the function
        self.namespace = naming.Namespace(parent_namespace=self.identifier.ns)
        self.locals['request'] = self.namespace.new_identifier('request', ref="VIEW.REQUEST")
        self.locals['page_context'] = self.namespace.new_identifier('page_context')
        if args is None:
            args = []
        self.args = [ (self.namespace.new_identifier(arg, ref=data['ref']), data) for arg, data in args ]

        # continuing args, make a namespace for page context
        self.pc_namespace = naming.Namespace()
        for arg, data in self.args:
            name_attempt = data.get('template_id', 'BADNAME') # helps a test pass
            data['template_id'] = self.pc_namespace.new_identifier(str(name_attempt), ref=data['ref'])

        # queries
        self.queries = []
        if queries is None:
            queries = []
        for q_obj in queries:
            self.add_query(q_obj)

        self.template_code_path = template_code_path

        # search
        if self.has_search:
            self.search_code_path = "search.html"

        # access level
        self.login_required = False
        if access == 'users':
            self.login_required = True

    def add_query(self, dq_obj):
        template_id = self.pc_namespace.new_identifier('%ss' % dq_obj.model_id, ref=dq_obj) # very crude pluralize
        self.queries.append((template_id, dq_obj.render()))

    def render(self):
        return env.get_template('view.py').render(view=self, imports=self.namespace.imports(), locals=self.locals)


class DjangoFormReceiver(object):

    def __init__(self, identifier, form_id, redirect=True):
        """
        For now it'll only work with fields that are directly associate with the model
        """
        self.identifier = identifier
        self.namespace = naming.Namespace(parent_namespace=self.identifier.ns)
        self.locals = {'request': self.namespace.new_identifier('request'),
                       'redirect_url': self.namespace.new_identifier('redirect_url')}
        self.form_id = form_id
        self.code_path = 'webapp/form_receivers.py'

        self.redirect = redirect

    def render(self):
        return env.get_template('form_receiver.py').render(fr=self, imports=self.namespace.imports(), locals=self.locals)


class DjangoCustomFormReceiver(DjangoFormReceiver):

    def __init__(self, saved_thing_id, *args, **kwargs):
        super(DjangoCustomFormReceiver, self).__init__(*args, **kwargs)
        self.args = []
        self.locals['obj'] = self.namespace.new_identifier(saved_thing_id)
        self.pre_relation_assignments = []
        self.relation_assignments = []
        self.commit = True
        self.after_save_saves = []

    def add_args(self, args):
        args = [ (self.namespace.new_identifier(arg, ref=data['ref']), data) for arg, data in args ]
        for arg, data in args:
            name_attempt = data.get('inst_id', 'BADNAME') # helps a test pass
            data['inst_id'] = self.namespace.new_identifier(str(name_attempt), ref=data['ref']) 
        self.args.extend(args)


    def render(self):
        return env.get_template('form_receiver_custom_1.py').render(fr=self, imports=self.namespace.imports(), locals=self.locals)


class DjangoLoginFormReceiver(DjangoFormReceiver):

    def add_role_redirect(self, role_redirect):
        assert not hasattr(self, 'role_redirect'), "There were multiple login with facebook buttons in the app. Butwai."
        self.role_redirect = role_redirect

    def render(self):
        return env.get_template('login_form_receiver.py').render(fr=self, imports=self.namespace.imports(), locals=self.locals)


class DjangoSignupFormReceiver(DjangoFormReceiver):

    """
    def __init__(self, identifier, user_profile_form_id):
        super(DjangoSignupFormReceiver, self).__init__(identifier)
        #self.user_profile_form_id = user_profile_form_id
        """

    def add_signup_role(self, role_name, role_field_id):
        self.locals['role_field_id'] = role_field_id
        self.signup_role = role_name

    def render(self):
        return env.get_template('signup_form_receiver.py').render(fr=self, imports=self.namespace.imports(), locals=self.locals)
