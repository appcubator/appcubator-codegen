import re

from app_builder.analyzer import datalang, pagelang
from app_builder.codes import DjangoModel, DjangoUserModel
from app_builder.codes import DjangoPageView, DjangoTemplate, DjangoPageSearch, SocialAuthHandler
from app_builder.codes import DjangoURLs, DjangoStaticPagesTestCase, DjangoQuery
from app_builder.codes import DjangoForm, DjangoFormReceiver, DjangoCustomFormReceiver
from app_builder.codes import DjangoLoginForm, DjangoLoginFormReceiver, DjangoSignupFormReceiver
from app_builder.codes.utils import AssignStatement, FnCodeChunk, RoleRedirectChunk
from app_builder.imports import create_import_namespace
from app_builder import naming


class AppComponentFactory(object):

    def __init__(self):

        self.model_namespace = create_import_namespace('webapp/models.py')
        self.form_namespace = create_import_namespace('webapp/forms.py')
        self.view_namespace = create_import_namespace('webapp/pages.py')
        self.fr_namespace = create_import_namespace('webapp/form_receivers.py')
        self.urls_namespace = create_import_namespace('webapp/urls.py')
        self.tests_namespace = create_import_namespace('webapp/tests.py')

        self.userrole_namespace = naming.Namespace()

    def setup_userrole_namespace(self, app):
        for role in app.userentity.role_names:
            self.userrole_namespace.new_identifier(role, ref=role)
        app.userentity.get_role_id = lambda x: self.userrole_namespace.get_by_ref(x)

    # MODELS

    def create_model(self, entity):
        """
        Creates DjangoModel and the non relational fields for it.
        Additionally, deals with User model separately.
        """
        if entity.is_user:
            user_identifier = self.model_namespace.get_by_import('django.models.User')
            user_profile_identifier = self.model_namespace.new_identifier('UserProfile', cap_words=True)
            m = DjangoUserModel(user_identifier, user_profile_identifier)
            # fields are split into user fields and user profile fields
            # add userprofile fields to the model
            for f in filter(lambda x: not x.is_relational(), entity.user_profile_fields):
                # has the side effect of adding it to the model, so don't worry about that.
                df = m.create_field(f.name, f.type, False) # make all field not required by default.
                            # the django model will create an identifier based on
                            # the name
                f._django_field_identifier = df.identifier
                f._django_field = df
            # bind identifiers to the built-in user fields.
            for f in entity.user_fields:
                x = {'username': 'username',
                     'First Name': 'first_name',
                     'Last Name': 'last_name',
                     'Email': 'email',
                    }
                f._django_field_identifier = x[f.name]

        else:
            identifier = self.model_namespace.new_identifier(entity.name, cap_words=True)
            m = DjangoModel(identifier)

            for f in filter(lambda x: not x.is_relational(), entity.fields):
                # has the side effect of adding it to the model, so don't worry about that.
                df = m.create_field(f.name, f.type, False) # fields are not required by default.
                            # the django model will create an identifier based on
                            # the name
                f._django_field_identifier = df.identifier
                f._django_field = df

        # add audit fields.
        cf = m.add_date_created_field(self.model_namespace.new_identifier('date_created'))
        entity.created_field = cf
        mf = m.add_date_modified_field(self.model_namespace.new_identifier('date_modified'))
        entity.modified_field = mf

        # set references
        entity._django_model = m
        m._entity = entity
        return m

    def create_relational_fields_for_model(self, entity):
        m = entity._django_model

        for f in filter(lambda x: x.is_relational(), entity.fields):
            # get the related django model's id (from the imports.)
            rel_model = f.entity._django_model
            rel_model_id = rel_model.identifier
            # make an id for the related name in the related model's namespace
            # TODO FIXME potential bugs with related name and field name since they are really injected into the model.Model instance namespace
            rel_name_id = rel_model.namespace.new_identifier(f.related_name, ref=rel_model)

            quote = not f.entity.is_user
            df = m.create_relational_field(f.name, f.type, rel_model_id, rel_name_id, False, quote=quote)
                        # the django model will create an identifier based on
                        # the name
            f._django_field_identifier = df.identifier
            f._django_field = df

    def import_model_into_namespace(self, entity, namespace):
        if namespace == 'views':
            ns = self.view_namespace
        elif namespace == 'forms':
            ns = self.form_namespace
        elif namespace == 'form receivers':
            ns = self.fr_namespace
        elif namespace == 'tests':
            ns = self.tests_namespace
        else:
            raise KeyError

        m = entity._django_model
        import_symbol = ('webapp.models', m.identifier)
        ns.find_or_create_import(import_symbol, m.identifier)


    # VIEWS

    def create_view_for_page(self, page):
        identifier = self.view_namespace.new_identifier(page.name)

        args = []
        for e in page.get_tables_from_url():
            model_id = e._django_model.identifier
            template_id = model_id
            args.append((e.name.lower()+'_id', {"model_id": model_id, "template_id": template_id, "ref": e._django_model}))

        v = DjangoPageView(identifier, args=args, access=page.access_level)
        page._django_view = v
        return v

    def find_or_create_query_for_view(self, uie):

        entity = uie.container_info.entity_resolved
        query = uie.container_info.query
        # create a list of keyvalue pairs for the filter in the query
        filter_key_values = []
        page = uie.page
        view = page._django_view

        for where_clause in query.where:
            key = where_clause.field._django_field.identifier
            def gen_code_for_value():
                x = where_clause.equal_to_dl.to_code(context=view.pc_namespace) # pass the page context
                if where_clause.equal_to_dl.result_type == 'object':
                    return "%s.id" % x
                return x
            value = gen_code_for_value
            filter_key_values.append((key, FnCodeChunk(value)))

        sort_by_id = None
        # TODO(nkhadke): HACK right now. Add sort validation + -ves??
        sort_by_id = "date_created"
        # sort_by_id = FnCodeChunk(lambda: '-%s' % entity.created_field.identifier)

        dq = DjangoQuery(entity._django_model.identifier, where_data=filter_key_values,
                                                          sort_by_id=sort_by_id,
                                                          limit=query.numberOfRows)

        view.add_query(dq)

        uie._django_query = dq
        uie._django_query_id = view.pc_namespace.get_by_ref(dq)

        #return dq


    # HTML GEN

    def properly_name_variables_in_template(self, page):
        def oneshot_datalang(s, req_handler):
            """
            Given a string and a request handler:
                1. create datalang
                2. find the context
                3. return the result of to_code of the datalang
            """
            dl = datalang.parse_to_datalang(s, page.app)
            return dl.to_code(context=page._django_view.pc_namespace)

        def translate(m):
            return "{{ %s }}" % oneshot_datalang(m.group(1).strip(), page._django_view)

        translate_all = lambda x: re.sub(r'\{\{ ?([^\}]*) ?\}\}', translate, x)

        for uie in page.uielements:
            uie.visit_strings(translate_all)

    def create_tree_structure_for_page_nodes(self, page):
        """
        Given a page, returns a django template which has references
        to the page's uielements. The resulting tree uses the layout of
        the uielements to create the layout of the page and
        it positions the uielements relative to their containers.

        """
        t = DjangoTemplate(page._django_view.identifier)
                            # this is an underscore-name, so it should be good as a filename
        t.create_tree(page.uielements)
        t.page = page
        page._django_template = t
        page._django_view.template_code_path = t.filename
        return t


    # URL NAMESPACES

    def create_urls(self, app):
        url_patterns_id = self.urls_namespace.new_identifier('urlpatterns', ref='MISC.urlpatterns')
        u = DjangoURLs('webapp.pages', self.urls_namespace, url_patterns_id, first_time=True)
        app._django_page_urls = u
        return u

    def create_fr_urls(self, app):
        url_patterns_id = self.urls_namespace.get_by_ref('MISC.urlpatterns')
        u = DjangoURLs('webapp.form_receivers', self.urls_namespace, url_patterns_id, first_time=False)
        app._django_fr_urls = u
        return u

    def create_misc_urls(self, app):
        url_patterns_id = self.urls_namespace.get_by_ref('MISC.urlpatterns')
        u = DjangoURLs('', self.urls_namespace, url_patterns_id)
        app._django_misc_urls = u
        return u



    # ADDING ROUTES

    def add_social_include_url(self, app):
        """
        End goal is this: url(r'', include('social_auth.urls')),
        """
        url_obj = app._django_misc_urls
        social_incl_identifier = FnCodeChunk(lambda: '%s("social_auth.urls")' % self.urls_namespace.imports()['django.include'])
        social_include_route = ("r''", social_incl_identifier)
        url_obj.routes.append(social_include_route)

    def add_logout_url(self, app):
        """End goal is this: url('^logout/$', logout, {"next_page" : "/"}),"""
        url_obj = app._django_misc_urls
        logout_id = self.urls_namespace.imports()['django.auth.logout_view'] # TODO use the import instead.
        kwargs = { "next_page": "/" }
        logout_route = ("""r'^__logout/$'""", logout_id, kwargs)
        url_obj.routes.append(logout_route)

    def add_search_url(self, app):
        """Adds the generic search route to webapp.pages: url('^search/$', 'search'),"""
        url_obj = app._django_page_urls
        search_route = ("""r'^search/$'""", "'search'")
        url_obj.routes.append(search_route)

    def add_page_to_urls(self, page):
        url_obj = page.app._django_page_urls

        route = (page.url_regex, FnCodeChunk(lambda: "'%s'" % page._django_view.identifier))
        url_obj.routes.append(route)

    def create_url_for_form_receiver(self, uie):
        url_obj = uie.app._django_fr_urls

        url = self.urls_namespace.new_identifier(uie._django_form.identifier)
        route = (repr('^%s/$' % url), FnCodeChunk(lambda: "'%s'" % uie._django_form_receiver.identifier))
        url_obj.routes.append(route)

        # this assumes the form receiver is the this module
        data_string = ' '.join(['{{ Page.%s }}.id' % e.name for e in uie.container_info.form.get_needed_page_entities()]) # result should be something like "{{ Page.Book }}.id {{ Page.Class }}.id"
        if data_string != '':
            data_string += ' ' # just for formatting.
        uie.set_post_url('{%% url webapp.form_receivers.%s %s%%}' % (uie._django_form_receiver.identifier, data_string))


    # FORMS

    def create_django_form_for_entity_based_form(self, uie):
        form_model = uie.container_info.form # bind to this name to save me some typing
        if form_model.action not in ['create', 'edit']:
            return None
        prim_name = form_model.action + '_' + form_model.entity_resolved.name
        form_id = self.form_namespace.new_identifier(prim_name, cap_words=True)
        model_id = form_model.entity_resolved._django_model.identifier
        field_ids = []
        for f in form_model.fields:
            try:
                assert not f.is_relational()
                field_ids.append(f.model_field._django_field_identifier)
            except AttributeError:
                pass
        form_obj = DjangoForm(form_id, model_id, field_ids)
        uie._django_form = form_obj
        return form_obj


    def add_search_functionality(self, page):
        ps = DjangoPageSearch(self.view_namespace.new_identifier(page.name))
        return ps

    def create_login_form_if_not_exists(self, uie):
        if hasattr(self, '_django_login_form'):
            form_obj = self._django_login_form
        else:
            prim_name = 'LoginForm'
            form_id = self.form_namespace.find_or_create_import('django.forms.AuthForm', prim_name)
            form_obj = DjangoLoginForm(form_id)

        uie._django_form = form_obj
        return form_obj

    def create_signup_form_if_not_exists(self, uie):
        if hasattr(self, '_django_signup_form'):
            form_obj = self._django_signup_form
        else:
            prim_name = 'SignupForm'
            form_id = self.form_namespace.find_or_create_import('django.forms.UserCreationForm', prim_name)
            form_obj = DjangoLoginForm(form_id)
        uie._django_form = form_obj
        return form_obj


    ## FORM RECEIVERS

    def create_role_redirect_chunk_from_login_routes(self, loginRoutes, app):
        def create_tuple_from_loginroute(r):
            role = r.role
            fn = FnCodeChunk(lambda: r.goto_pl.to_code(template=False))
            return (role, fn)
        role_linklang_tuples = [ create_tuple_from_loginroute(r) for r in loginRoutes ]
        role_field_id = app.user_role_field._django_field.identifier
        rr = RoleRedirectChunk(role_linklang_tuples, role_field_id)
        return rr

    def create_login_form_receiver_if_not_created(self, uie):
        if hasattr(self, '_django_login_form_receiver'):
            fr = self._django_login_form_receiver
        else:
            fr_id = self.fr_namespace.new_identifier('Login')
            if 'django.auth.login' not in self.fr_namespace.imports():
                self.fr_namespace.find_or_create_import('django.auth.login', 'auth_login')
            fr = DjangoLoginFormReceiver(fr_id, uie._django_form.identifier, redirect=uie.container_info.form.redirect)
            if uie.container_info.form.redirect:
                fr.locals['redirect_url_code'] = lambda: uie.container_info.form.goto_pl.to_code(template=False)

            # construct a roleredirect thing
            if uie.app.multiple_users:
                rr = self.create_role_redirect_chunk_from_login_routes(uie.container_info.loginRoutes, uie.app)
                fr.add_role_redirect(rr)

        uie._django_form_receiver = fr
        return fr

    def create_signup_form_receiver_if_not_created(self, uie):
        if hasattr(self, '_django_signup_form_receiver'):
            fr = self._django_signup_form_receiver
        else:
            fr_id = self.fr_namespace.new_identifier('Sign Up')
            if 'django.auth.login' not in self.fr_namespace.imports():
                self.fr_namespace.find_or_create_import('django.auth.login', 'auth_login')
            if 'django.auth.authenticate' not in self.fr_namespace.imports():
                self.fr_namespace.find_or_create_import('django.auth.authenticate', 'authenticate')
            fr = DjangoSignupFormReceiver(fr_id, uie._django_form.identifier, redirect=uie.container_info.form.redirect)
            if uie.container_info.form.redirect:
                fr.locals['redirect_url_code'] = lambda: uie.container_info.form.goto_pl.to_code(template=False)
            if uie.app.multiple_users:
                role_field_id = uie.app.user_role_field._django_field.identifier
                fr.add_signup_role(self.userrole_namespace.get_by_ref(uie.container_info.form.signupRole), role_field_id)
        uie._django_form_receiver = fr
        return fr

    def create_url_for_form_receiver_if_not_created(self, uie):
        url_obj = uie.app._django_fr_urls
        for url, identifier in url_obj.routes:
            if identifier.ref == uie._django_form_receiver:
                return None
        return self.create_url_for_form_receiver(uie)

    def create_url_for_socialauth_login_handler_if_not_created(self, uie):
        if hasattr(self, 'social_auth_handler_url'):
            return

        url_obj = uie.app._django_fr_urls

        route = (repr('^___social_auth_callback/$'), FnCodeChunk(lambda: "'%s'" % self.social_auth_handler.identifier))
        self.social_auth_handler_url = route
        url_obj.routes.append(route)
        return url_obj

    def create_socialauth_login_handler_if_not_exists(self, uie):

        # find or create socialauth login_handler
        if hasattr(self, 'social_auth_handler'):
            sh = self.social_auth_handler
            created = False
        else:
            sh_id = self.fr_namespace.new_identifier('socialauth_success_callback')
            role_field_id = uie.app.user_role_field._django_field.identifier
            sh = SocialAuthHandler(sh_id, role_field_id)
            self.social_auth_handler = sh
            created = True

        # modify the handler to add the new information in this uie
        # add the role redirect chunk
        if uie.action == 'login':
            rr = self.create_role_redirect_chunk_from_login_routes(uie.loginRoutes, uie.app)
            sh.add_role_redirect(rr)

        # add the mapping from this signup role to goto_pl to either this or the existing handler
        else:
            assert uie.action =='signup', "social action not supported: %r" % uie.action
            sh.add_signup_role_redirect(uie.app.userentity.get_role_id(uie.signupRole), uie.goto_pl)

        # return only if new hander was actually created here.
        return sh if created else None


    def resolve_page_and_its_datalang(self, uie):
        def resolve_pagelang(pagelang_str):
            try:
                resolved_ps = pagelang.parse_to_pagelang(pagelang_str, uie.app).to_code(context=uie.page._django_view.pc_namespace)
                return resolved_ps
            except AssertionError:
                return pagelang_str
        uie.visit_strings(resolve_pagelang)

    def import_form_into_form_receivers(self, uie):
        f = uie._django_form
        import_symbol = ('webapp.forms', f.identifier)
        self.fr_namespace.find_or_create_import(import_symbol, f.identifier)

    def create_form_receiver_for_form_object(self, uie):
        fr_id = self.fr_namespace.new_identifier(uie._django_form.identifier)
        form_model = uie.container_info.form
        thing_id = form_model.entity_resolved.name
        fr = DjangoCustomFormReceiver(thing_id, fr_id, uie._django_form.identifier, redirect=form_model.redirect)
        args = []
        for e in uie.container_info.form.get_needed_page_entities():
            model_id = e._django_model.identifier
            inst_id = str(model_id) # Book inst should just be called book. lower casing happens in naming module
            args.append((e.name.lower()+'_id', {"model_id": model_id, "ref": e._django_model, "inst_id": inst_id})) 
        fr.locals['obj'].ref = uie.container_info.form.entity_resolved
        if form_model.redirect:
            fr.locals['redirect_url_code'] = lambda: uie.container_info.form.goto_pl.to_code(context=fr.namespace, template=False, seed_id=fr.locals['obj'])
        fr.add_args(args)
        uie._django_form_receiver = fr
        return fr

    def add_relation_assignments_to_form_receiver(self, uie):
        form_model = uie.container_info.form # bind to this name to save me some typing
        fr = uie._django_form_receiver

        def translate(s):
            dl = datalang.parse_to_datalang(s, uie.app)
            return dl.to_code(seed_id=fr.locals['obj'])

        if form_model.action not in ['create', 'edit']:
            return None
        # figure out which LHS things need to be bound to an identifier.
        # more than 1 dot => needs binding!
        new_var_map = {}
        after_save_saves = []
        commit = True
        for l, r in form_model.get_actions_as_tuples():
            # translate and evalute the left side for some analysis
            translated_l = translate(l)
            toks = translated_l.split('.')
            if len(toks) > 2:
                attr = toks[-1]
                new_bind_name = fr.namespace.new_identifier('%s parent' % attr) # todo put type of obj
                a = AssignStatement(new_bind_name, FnCodeChunk(lambda: '.'.join(str(translate(l)).split('.')[:-1])))
                fr.pre_relation_assignments.append(a)
                new_var_map[l] = FnCodeChunk(lambda: '%s.%s' % (new_bind_name, attr))

            a = AssignStatement(new_var_map.get(l, translate(l)), translate(r))
            fr.relation_assignments.append(a)

            # if the object created by the form is modified in relations, then commit=False
            if l.startswith('Form.'):
                commit = False
            # if other objects are modified, then save them.
            else:
                after_save_saves.append(FnCodeChunk(lambda: '.'.join(str(new_var_map.get(l, translate(l))).split('.')[:-1])))


        if not commit:
            fr.commit = False

        fr.after_save_saves = after_save_saves




    # TESTS

    def create_tests_for_static_pages(self, app):
        ident_url_pairs = []
        for p in app.pages:
            if p.is_static():
                ident_url_pairs.append((p._django_view.identifier, '/' + ''.join([x + '/' for x in p.url.urlparts])))
        d = DjangoStaticPagesTestCase(ident_url_pairs, self.tests_namespace)
        return d
