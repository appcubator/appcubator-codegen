from app_builder.coder import Coder
from app_builder.create_functions import AppComponentFactory
from pyflakes.api import check

import logging
import traceback
import logging

logger = logging.getLogger('app_builder.controller')

logger = logging.getLogger("codegen-controller")


def create_codes(app):
    factory = AppComponentFactory()

    create_map = {# MODELS
                  'setup user roles namespace': factory.setup_userrole_namespace,
                  'create model for entity': factory.create_model,
                  'create relational fields for entity': factory.create_relational_fields_for_model,
                  'import model into views': lambda entity: factory.import_model_into_namespace(entity, 'views'),
                  'import model into forms': lambda entity: factory.import_model_into_namespace(entity, 'forms'),
                  'import model into form receivers': lambda entity: factory.import_model_into_namespace(entity, 'form receivers'),
                  'import model into tests': lambda entity: factory.import_model_into_namespace(entity, 'tests'),
                  'register model with admin site': factory.register_model_with_admin,

                  # INITING FOR URLS
                  'create urls object for app': factory.create_urls,
                  'create urls object for app form receivers': factory.create_fr_urls,
                  'create misc urls object for app': factory.create_misc_urls,
                  'add social include url': factory.add_social_include_url,
                  "create url for socialauth login handler if not created": factory.create_url_for_socialauth_login_handler_if_not_created,
                  'add logout url': factory.add_logout_url,
                  'add search url' : factory.add_search_url,
                  'add admin urls' : factory.add_admin_urls,

                  # GET REQUEST HANDLERS
                  'view for page': factory.create_view_for_page,
                  'url to serve page': factory.add_page_to_urls,
                  'find or add the needed data to the view': factory.find_or_create_query_for_view ,
                  'find or add the needed search to the view': factory.find_or_create_search_for_view ,
                  'create socialauth login handler': factory.create_socialauth_login_handler_if_not_exists,

                  # PAGE AND DATALANG
                  'resolve links href' : factory.resolve_page_and_its_datalang,

                  # Search
                  'search code generation' : factory.add_search_functionality,

                  # HTML GEN STUFF
                  'translate strings in uielements': factory.properly_name_variables_in_template,
                  'create row/col structure for nodes': factory.create_tree_structure_for_page_nodes,
                  'create tests for static pages': factory.create_tests_for_static_pages,

                  # ENTITY FORM RELATED HOOKS
                  'create form object': factory.create_django_form_for_entity_based_form,
                  'create form receiver': factory.create_form_receiver_for_form_object,
                  'create url for form receiver': factory.create_url_for_form_receiver,
                  'import form into form receivers': factory.import_form_into_form_receivers,
                  # I put this in import form into the create url step 'set post url for form': factory.set_post_url_for_form,
                  'add the relation things to the form recevier': factory.add_relation_assignments_to_form_receiver,

                  # USER FORM RELATED HOOKS
                  'create login form if not exists': factory.create_login_form_if_not_exists,
                  'create signup form if not exists': factory.create_signup_form_if_not_exists,
                  'create login form receiver if not exists': factory.create_login_form_receiver_if_not_created,
                  'create signup form receiver if not exists': factory.create_signup_form_receiver_if_not_created,
                  'create url for form receiver if not created': factory.create_url_for_form_receiver_if_not_created,
    }


    codes = []

    def create(event_name, el, *args, **kwargs):
        try:
            logger.info("Running hook: %s" % event_name)
            c = create_map[event_name](el)
        except KeyError:
            raise
        else:
            if c is not None:
                codes.append(c)

    # setup models
    for ent in app.tables:
        create('create model for entity', ent) # only creates primitive fields
    for ent in app.tables: # doing relational fields after because all models need to be created for relations to work
        create('create relational fields for entity', ent)
        create('register model with admin site', ent)
        create('import model into views', ent)
        create('import model into forms', ent)
        create('import model into form receivers', ent)
        create('import model into tests', ent)

    create('setup user roles namespace', app)

    # routes and functions to serve pages
    create('create urls object for app', app)
    create('create urls object for app form receivers', app)
    create('create misc urls object for app', app)
    create('add social include url', app)
    create('add admin urls', app)
    create('add logout url', app)
    for p in app.pages:
        create('view for page', p)
        create('url to serve page', p)

    # UIELEMENT HOOKS
    for p in app.pages:
        for uie in p.uielements:
            for hook_name in uie.hooks:
                try:
                    create(hook_name, uie)
                except Exception, e:
                    logger.error("Failed to call hook %r on %r instance" % (hook_name, uie.__class__.__name__))
                    traceback.print_exc()
                    raise

    # translation of {{ page.book.name }} to proper django template code
    for p in app.pages:
        create('translate strings in uielements', p)

    # create html nodes and structure for pages
    for p in app.pages:
        create('create row/col structure for nodes', p)

    # create('search rendering', app.pages[len(app.pages)-1])

    # random app-wide stuff
    create('create tests for static pages', app)

    return codes

def main(app):
    codes = create_codes(app)
    cc = Coder.create_from_codes(codes)

    for rel_path, code in cc.itercode():
        print "\n\n============ %s ============\n" % rel_path, code
        #if rel_path.endswith('.py'):
        #    print check(code, 'test.py')
    return (codes, cc)


"""
Sample actions include-
    render some page with some data
    redirect to another page with some data
    get noun from the DB with some query
    create, update, or delete some noun
    send an email to some user with some data

Result should be similar to an AST.
    actions=
    [
"""
