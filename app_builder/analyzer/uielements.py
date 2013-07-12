from dict_inited import DictInited
from resolving import Resolvable
from utils import encode_braces, decode_braces
from copy import deepcopy
from datetime import datetime
import simplejson
import re

from app_builder.htmlgen import Tag
from app_builder.analyzer.datalang import parse_to_datalang
from app_builder.codes import DjangoEmailTemplate

from . import env
from . import logger
from . import UserInputError
from . import assert_raise
from . import pagelang

def get_uielement_by_type(type_string):
    UIELEMENT_TYPE_MAP = {'form': Form,
                          'loop': Iterator,
                          'node': Node,
                          'thirdpartylogin' : ThirdPartyLogin,
                          'search' : Search,
                          'gallery': Gallery
                         }
    subclass = UIELEMENT_TYPE_MAP[type_string]
    return subclass


# this is used in uielements whenever redirects depend on the role.
class RoleRouting(DictInited, Resolvable):
    _schema = {
        "role": {"_type": ""}, # name of the user role (Student)
        "redirect": {"_type": ""} # link lang it should redirect to
    }
    _resolve_attrs = ()
    _pagelang_attrs = (('redirect', 'goto_pl'),)

    def validate(self):
        assert_raise(self.role in [u.name for u in self.app.users],
                UserInputError("This role was not recognized: %r Maybe you had it once and then deleted it?" % self.role, self._path))


class Layout(DictInited):
    _schema = {
        "width": {"_type": 0, "_min": 1}, # max is 64 unless this is in a row, b/c then it's absolutepositioned in px
        "height": {"_type": 0, "_min": 1},
        "top": {"_type": 0, "_min": 0}, # max is 64 unless this is in a row, b/c then it's absolutepositioned in px
        "left": {"_type": 0, "_min": 0}, # max is 64 unless this is in a row, b/c then it's absolutepositioned in px
        "t_padding": {"_type": 0, "_default": 0},
        "b_padding": {"_type": 0, "_default": 0},
        "l_padding": {"_type": 0, "_default": 0},
        "r_padding": {"_type": 0, "_default": 0},
        "alignment": {"_type": "", "_default": "left"},
        "font-size": {"_type": "", "_default": ""},
    }

    def has_padding(self):
        return self.t_padding > 0 or self.b_padding > 0 or self.l_padding > 0 or self.r_padding > 0


class UIElement(DictInited):
    _schema = {"layout": {"_type": Layout},
               "type": {"_type": ""}, # Specifies the type of the UIElement this represents.
               "data": {"_type": {}}} # An arbitrary dict, used to init a specific type of UIElement.

    def __init__(self, *args, **kwargs):
        """Uses type and data attributes to dynamically create the subclass"""
        super(UIElement, self).__init__(*args, **kwargs)
        try:
            subclass = get_uielement_by_type(self.type)
        except KeyError:
            raise Exception("Type not recognized: %r" % self.type)
        self.subclass = subclass.create_from_dict(self.data)
        self.subclass.layout = self.layout


class Hooked(object):

    @property
    def hooks(self):
        try:
            return self.__class__._hooks
        except AttributeError:
            return () # empty tuple


class Form(DictInited, Hooked):

    # these are tightly coupled and serial for now.
    _hooks = ('create form object',
              'import form into form receivers',
              'create form receiver',
              'create url for form receiver',
              'add the relation things to the form recevier',
              'add email actions to the form receiver',
              # add the url to the action attribute, this happens in the "create url" phase
             )

    @property
    def hooks(self):
        action = self.container_info.form.action
        if action not in ('login', 'signup'):
            return super(Form, self).hooks

        if action == 'login':
            return ('create login form if not exists',
                    'import form into form receivers',
                    'create login form receiver if not exists',
                    'create url for form receiver',
                    'add emails for non general form receivers'
                   )

        elif action == 'signup':
            return ('create signup form if not exists',
                    'import form into form receivers',
                    'create signup form receiver if not exists',
                    'create url for form receiver',
                    'add emails for non general form receivers'
                   )
        else:
            assert False, "Form action not recognized: %s" % action



    class FormInfo(DictInited):

        class FormInfoInfo(DictInited, Resolvable):

            class FormField(object):

                def htmls(field, edit_inst_code_fn=None):
                    base_attribs = {}
                    tagname = 'input'
                    content=None

                    # logic to set up the html data
                    if field.displayType.endswith('-text'):
                        base_attribs = {'type': 'text',
                                        'placeholder': field.placeholder,
                                        'name': field.backend_field_name
                                       }

                        if field.displayType == 'password-text':
                            base_attribs['type'] = 'password'

                        if field.displayType == 'paragraph-text':
                            del base_attribs['type']
                            tagname = 'textarea'

                        if edit_inst_code_fn is not None:
                            base_attribs['value'] = "{{ %s.%s }}" % (edit_inst_code_fn(), field.backend_field_name)
                            # don't use place holder if some edit value is going to be filled in anyway.
                            del base_attribs['placeholder']

                    elif field.displayType.endswith('-uploader'):
                        tagname = 'div'
                        class_string = 'upload-img btn' if field.displayType == 'image-uploader' else 'upload-file btn'

                        filepicker_button = Tag('div', {'class': class_string, 'data-name': field.backend_field_name}, content=field.placeholder)
                        # this is needed for ajaxify to put in the filepicker value, and for the browser to submit the form
                        real_input = Tag('input', {'type': 'hidden', 'name': field.backend_field_name })
                        if edit_inst_code_fn is not None:
                            real_input.attribs['value'] = "{{ %s.%s }}" % (edit_inst_code_fn(), field.backend_field_name)
                        content = [filepicker_button, real_input]

                    elif field.displayType == 'dropdown':
                        tagname = 'select'
                        opt_fields = []
                        for item in field.options:
                            opt_field = Tag('option', {'value': item}, content=item)
                            opt_fields.append(opt_field)
                        content = opt_fields
                        base_attribs['name'] = field.backend_field_name

                    elif field.displayType == 'option-boxes':
                        tagname = 'span'
                        opt_fields = []
                        for item in field.options:
                            opt_field_id = field._page.id_namespace.new_identifier('opt-label-%s' % field.backend_field_name)
                            opt_fields.append(Tag('input', {'id': opt_field_id, 'class': 'field-type', 'type': 'radio', 'name':field.backend_field_name}))
                            opt_fields.append(Tag('label', {'for': opt_field_id}, content=item))
                        content = opt_fields
                        base_attribs['name'] = field.backend_field_name
                        base_attribs['class'] = 'option-boxes'

                    elif field.displayType == 'date-picker':
                        tagname = 'div'
                        base_attribs['class'] = 'date-picker-wrapper'
                        inp = Tag('input', {'class': "date-picker-input", 'type': "text", 'name': field.backend_field_name}) # TODO find alternative to id-{name}
                        img = Tag('img', { 'class': "date-picker-icon"})
                        content = [inp, img]


                    elif field.displayType == 'button':
                        base_attribs['type'] = 'submit'
                        base_attribs['value'] = field.placeholder
                        base_attribs['class'] = 'btn'


                    # create the html
                    field_html = Tag(tagname, base_attribs, content=content)

                    htmls = []

                    # add a label if possible
                    try:
                        if field.label is not None:
                            label = Tag('label', {}, content=field.label)
                            htmls.append(label)
                    except AttributeError:
                        pass

                    htmls.append(field_html)
                    try:
                        error_div = Tag('div', {'class': 'form-error field-name-%s' % field.backend_field_name})
                        htmls.append(error_div)
                    except AttributeError:
                        pass

                    return htmls

            class FormModelField(FormField, DictInited, Resolvable):
                _schema = {
                    "field_name": {"_type": ""},
                    "required": {"_type": True, "_default": True},
                    "placeholder": {"_type": ""},
                    "label": {"_type": "", "_default": ""},
                    "displayType": {"_type": ""},
                    "options": {"_type": ""} # this is only used for dropdown and radio. it's split by comma in init. end type = list.
                }

                _resolve_attrs = (('field_name', 'model_field'),)

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.FormModelField, self).__init__(*args, **kwargs)
                    self.name = self.field_name
                    self.options = [ s.strip() for s in self.options.split(',') if s.strip() != "" ]
                    assert self.displayType != "button", "If this is a button, please remove the displayType, or the name, or options."

                def set_backend_name(self):
                    self.backend_field_name = self.model_field._django_field_identifier

            class FormNormalField(FormField, DictInited):
                _schema = {
                    "name": {"_type": ""},
                    "required": {"_type": True},
                    "placeholder": {"_type": ""},
                    "label": {"_type": ""},
                    "displayType": {"_type": ""},
                    "options": {"_type": ""} # this is only used for dropdown and radio. it's split by comma in init. end type = list.
                }

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.FormNormalField, self).__init__(*args, **kwargs)
                    self.options = [ s.strip() for s in self.options.split(',') if s.strip() != "" ]
                    assert self.displayType != "button", "If this is a button, please remove the displayType, or the name, or options."

                def set_backend_name(self):
                    self.backend_field_name = self.name

            class ButtonField(FormField, DictInited):
                _schema = {
                    # HACK - if you leave out the name attribute, it automatically becomes a button
                    "placeholder": {"_type": ""},
                }

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.ButtonField, self).__init__(*args, **kwargs)
                    self.displayType = 'button'

                def set_backend_name(self):
                    """Just for consistency w other fields"""
                    pass

            class EmailAction(DictInited):
                _schema = {
                    "email_to": {"_type": ""},
                    "nl_description": {"_type": ""},
                    "email": {"_type": ""}
                }

            class RelationalAction(DictInited):
                _schema = {
                    "set_fk": {"_type": ""},
                    "to_object": {"_type": ""}
                }
                # in the strings, "this" will refer to the instance of the entity being created in the form
                # set fk could be something like, "this.teacher" or "CurrentUser.mygroup".
                # to object could be something like, "Page.Teacher" or "Page.Group"

            _schema = {
                "entity": {"_type": ""},
                "action": {"_type": ""},
                "fields": {"_type": [], "_each": {"_one_of": [{"_type": FormModelField},{"_type": FormNormalField},{"_type": ButtonField}]}},
                "actions": {"_one_of": [
                                        {"_type": [], "_default": [], "_each": {"_type": RelationalAction}},
                                        {"_type": [], "_default": [], "_each": {"_type": EmailAction}}
                                        ]
                            },

                "loginRoutes": {"_one_of": [{"_type" : [], "_each": {"_type": RoleRouting}}, {"_type": None}], "_default": None},
                    # or (checked in validate, which is called in app's create from dict)
                "signupRole" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},
                "goto" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},
                "editOn" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},

            }

            _resolve_attrs = (('entity', 'entity_resolved'),)
            # overridden resolve_page function => goto_pl will only exist if redirect = True. see the code for that fn.
            _pagelang_attrs = (('goto', 'goto_pl'), )
            # overridden resolve_data function => edit_dl will only exist if editOn not none. see the code for that fn.
            _datalang_attrs = (('editOn', 'edit_dl'), )

            def __init__(self, *args, **kwargs):
                super(Form.FormInfo.FormInfoInfo, self).__init__(*args, **kwargs)
                for f in filter(lambda x: isinstance(x, Form.FormInfo.FormInfoInfo.FormModelField), self.fields):
                    f.field_name = encode_braces('tables/%s/fields/%s' % (self.entity, f.field_name))

            def validate(self):
                if self.action in ['login', 'signup']:
                    assert not (self.signupRole is None and self.loginRoutes is None), "signupRole and loginRoutes can't both be null."
                if self.action == 'login':
                    assert_raise(len(self.loginRoutes) == len(self.app.users),
                            UserInputError("You added or deleted a user role, so you need to update the redirecting post-login.", self._path + "/loginRoutes"))
                    assert self.goto is None, "Login form must use loginRoutes, not goto"
                else:
                    assert self.goto is not None, "All forms other than login form must have goto"

                if self.action == 'signup':
                    assert self.signupRole is not None, "signup form must have signupRole"
                    assert_raise(self.signupRole in [u.name for u in self.app.users],
                            UserInputError("You deleted a user role, so you need to update your signup form.", self._path + "/loginRoutes"))

                if self.action == 'edit':
                    assert self.editOn is not None, "Editform takes editOn arg."

            def resolve_page(self):
                if self.goto is None:
                    self.redirect = False
                else:
                    self.redirect = True
                    super(Form.FormInfo.FormInfoInfo, self).resolve_page()

            def resolve_data(self):
                if self.action == "edit":
                    super(Form.FormInfo.FormInfoInfo, self).resolve_data()
                else:
                    pass

            def get_email_actions(self):
                email_tuples = []
                for a in self.actions:
                    if isinstance(a, Form.FormInfo.FormInfoInfo.EmailAction):
                        email = self.app.find('emails/%s' % a.email, name_allowed=True)
                        from_email = "info@%s.appcubator.com" % self.app.name.lower()
                        # Each email is always internally represted as 5-tuple that consists of:
                        # (from_email : str, to_email : code, subject : string, plain text : str, email_template_file: DjangoEmailTemplate)
                        try:
                            to_email = parse_to_datalang(a.email_to, self.app).to_code() + ".email"
                        except DictInited.FindFailed:
                            raise UserInputError("Stale reference in datalang in email", self._path)
                        email_template = DjangoEmailTemplate(a.email, email.content)
                        email_tuple = (from_email, to_email, a.nl_description, "", email_template)
                        email_tuples.append(email_tuple)
                return email_tuples

            def get_relational_actions_as_tuples(self):
                ans = []
                for a in self.actions:
                    if isinstance(a, Form.FormInfo.FormInfoInfo.RelationalAction):
                        ans.append((a.set_fk, a.to_object))
                return ans

            def string_ref_to_inst_only(self, s):
                if s.startswith('Page') or s.startswith('Loop'):
                    return ''.join(s.split('.')[:2])
                return s.split('.')[0]


            def get_needed_page_entities(self):
                # collect all refs in actions
                data_refs = [ item for tup in self.get_relational_actions_as_tuples() for item in tup ]

                if self.action == 'edit':
                    data_refs.append(self.editOn) # the string version... it's ghetto but it works

                entities = []
                for ref in data_refs:
                    toks = ref.split('.')
                    if toks[0] == 'Page':
                        name_of_type_of_inst_needed_from_page = toks[1]
                        entity = self.app.find('tables/%s' % name_of_type_of_inst_needed_from_page, name_allowed=True)
                        entities.append(entity)
                return entities


        _schema = {
            "form": {"_type": FormInfoInfo}
        }

    _schema = {
        "container_info": {"_type": FormInfo},
        "class_name": {"_type": "", "_default":""}
    }

    def visit_strings(self, f):
        self.post_url = f(self.post_url, template=False)

    def set_post_url(self, url):
        self.post_url = url

    def html(self):
        fields = ['{% csrf_token %}']
        for f in self.container_info.form.fields:
            # put the django model name in.
            f.set_backend_name()
            edit_inst_code_fn = None
            if self.container_info.form.action == 'edit':
                edit_dl = self.container_info.form.edit_dl
                edit_inst_code_fn = lambda: edit_dl.to_code(context=self.page._django_view.pc_namespace)
            fields.extend(f.htmls(edit_inst_code_fn=edit_inst_code_fn))
        fields.append(Tag('div', {'class': 'form-error field-all'}))
        post_url = self.post_url
        attribs = {'method': 'POST',
                   'action': post_url,
                   'class': self.class_name}
        form = Tag('form', attribs, content=fields)
        return form

class ThirdPartyLogin(DictInited, Hooked, Resolvable):
    """ Represents all third party logins: [linkedin, facebook, twitter]
            aight, the way it'll work is, the button will pass login vs. signup as GET params, and try to authenticate via facebook
            if success, it'll redirect to a custom handler
            then, based on the login vs success, and whether _role is Null, it'll do some actions
            in the login case where the user has not signed up (role is null), it'll delete the user that was created in the FB button process, and redirect to home
            in the signup case where the user is already signed up, it'll redirect to home.
            other cases work as expected """

    _hooks = ["create socialauth login handler",
              "create url for socialauth login handler if not created"]

    _schema = {
        "provider": {"_type" : ""},
        "content" : {"_type" : ""},

        "loginRoutes": {"_one_of": [{"_type" : [], "_each": {"_type": RoleRouting}}, {"_type": None}], "_default": None},
                # or (checked in validate, which is called in app's create from dict)
        "signupRole" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},
        "goto" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},
    }

    _resolve_attrs = ()
    _pagelang_attrs = (('goto', 'goto_pl'), )

    def __init__(self, *args, **kwargs):
        super(ThirdPartyLogin, self).__init__(*args, **kwargs)
        assert self.provider in ['facebook', 'twitter', 'linkedin'], "Invalid provider: %r" % self.provider
        # set up the action, just in case this is multi-user.
        # if single user, then action is completely ignored by codegen backend.
        if self.signupRole is not None:
            self.action = 'signup'
        elif self.loginRoutes is not None:
            self.action = 'login'
        else: assert False, "So is this signup or login?"

    def validate(self):
        assert not (self.signupRole is None and self.loginRoutes is None), "signupRole and loginRoutes can't both be null."
        if self.app.multiple_users:
            if self.action == 'signup':
                assert self.signupRole in [u.name for u in self.app.users]
                assert self.goto is not None
        elif self.action != 'signup':
            assert_raise(len(self.loginRoutes) == len(self.app.users), UserInputError("Please update the role-based redirect actions on the signup form.", self._path))
        else:
            assert_raise(False, UserInputError("Please remove the social signup button and drag the generic login/signup button instead.", self._path))

    def resolve_page(self):
        if self.action == 'login':
            pass
        else:
            super(ThirdPartyLogin, self).resolve_page()

    def query_string(self):
        query_string = "?action=%s" % self.action
        if self.action == 'signup':
            query_string += "&role=%s" % self.app.userentity.get_role_id(self.signupRole)
        return query_string

    def html(self):
        tpl_template = env.get_template('thirdpartylogin.html')
        tpl = Tag('div', {}, content=tpl_template.render(context=self))
        return tpl

    def visit_strings(self, f):
        pass

class Search(DictInited, Hooked):
    """ Wrapper class for search """

    _hooks = ["search code generation"]

    class SearchBox(DictInited, Resolvable):

        _schema = {
            'searchOn' : {"_type" : ""},
            'searchPage' : {"_type" : ""},
            'searchFields' : {
                "_type" : [], "_each": {"_type": ""}
            }
        }

        _pagelang_attrs = (("searchPage", "searchPageResolved"),)

        _resolve_attrs = (("searchFields", "searchFieldsResolved"),
                          ("searchOn", "searchOnResolved"))

        def __init__(self, *args, **kwargs):
            super(Search.SearchBox, self).__init__(*args, **kwargs)
            self.searchFields = [encode_braces('tables/%s/fields/%s' % (self.searchOn, fname)) for fname in self.searchFields]
            self.searchOn = encode_braces('tables/%s' % self.searchOn)

        def validate(self):
            assert not self.searchPageResolved.is_external

    def html(self):
        list_of_field_ids = [unicode(f._django_field_identifier) for f in self.searchQuery.searchFieldsResolved]
        self.field_json = simplejson.dumps(list_of_field_ids)
        tpl_template = env.get_template('search_box.html')
        self.searchMethod = "search_%s" % self.searchQuery.searchOnResolved.name.lower()
        tpl = Tag('div', {}, content=tpl_template.render(context=self))
        return tpl

        def visit_strings(self, f):
            # TODO butwhy is this here?
            self.searchPage = self.searchPage.lower()

    _schema = {"searchQuery" : {"_type" : SearchBox }}

    def visit_strings(self, f):
        pass

class Node(DictInited, Hooked):  # a uielement with no container_info
    _hooks = ['resolve links href']

    _schema = {
        "content": {"_default": None, "_one_of": [{"_type": None}, {"_type": "", "_default": ""}]},
        "content_attribs": {"_type": {}},
        "class_name": {"_type": ""},
        "tagName": {"_type": ""},
    }

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if self.content is None:
            self.content = ""

    def validate(self):
        v = lambda s: pagelang.parse_to_pagelang(s, self.app)
        v2 = lambda s: pagelang.parse_to_datalang(s, self.app)

        val_strings = []
        try:
            link_href = self.content_attribs['href']
            val_strings.append(link_href)
        except KeyError:
            pass
        try:
            img_src = self.content_attribs['src']
            val_strings.append(img_src)
        except KeyError:
            pass

        for s in val_strings:
            if s.startswith('http://') or s.startswith('https://'):
                pass
            elif s.startswith('internal'):
                try:
                    v(s)
                except DictInited.FindFailed:
                    raise UserInputError("Link has stale reference.", self._path)
                except pagelang.UrlDataMismatch:
                    raise UserInputError("Link doesn't give the right url data for the referenced page.", self._path)
            elif s.startswith('{{'):
                def test_v2(m):
                    try:
                        v2(m.group(1))
                    except DictInited.FindFailed:
                        raise UserInputError("Stale reference in datalang", self._path)
                    return "" # makes re.sub happy
                v2_wrap = lambda x: re.sub(r'\{\{ ?([^\}]*) ?\}\}', test_v2, x)
                v2_wrap(s)
            elif s == '/static/img/placeholder.png':
                pass
            else:
                assert False, "This is not a valid src or href value: %r. It should be external link, pagelang, or datalang." % s

    def kwargs(self):
        kw = {}
        kw = deepcopy(self.content_attribs)
        kw['class'] = 'node ' + self.class_name
        return kw

    def visit_strings(self, f):
        # Resolves either images or URLs
        self.content = f(self.content)
        try:
            if isinstance(self.content_attribs['src'], basestring):
                content = self.content_attribs['src']
                self.content_attribs['src'] = f(content)
        except KeyError:
            pass
        try:
            if isinstance(self.content_attribs['href'], basestring):
                self.content_attribs['href'] = f(self.content_attribs['href'])
        except KeyError:
            pass


    def html(self):
        try:
            content = self.content()
        except TypeError:
            content = self.content
        tag = Tag(self.tagName, self.kwargs(), content=content)
        if self.tagName == 'img':
            # wrap in div, except link, then wrap in a.
            if 'href' in self.kwargs():
                wrapper = Tag('a', {}, content=tag)
            else:
                wrapper = Tag('div', {}, content=tag)
            tag = wrapper
        return tag

class Gallery(DictInited, Hooked):  # a uielement with no container_info
    _hooks = ['resolve links href']

    class GalleryInfo(DictInited):
        class Image(DictInited):
            _schema = {
                "image": {"_type": ""},
                "text": {"_type": ""}
            }
        _schema = {
            "action": {"_type": ""},
            "slides": {"_type": [], "_each": {"_type": Image}},
            "uielements": {"_type": [], "_each": {"_type": UIElement}}
        }

    _schema = {
        "container_info": {"_type": GalleryInfo},
        "content_attribs": {"_type": {}}
    }

    def __init__(self, *args, **kwargs):
        super(Gallery, self).__init__(*args, **kwargs)
        timeid = unicode(datetime.now().microsecond)
        self.galleryid = "imageslider" + timeid

    def kwargs(self):
        kw = {}
        kw = deepcopy(self.content_attribs)
        kw["id"] = self.galleryid
        kw["class"] = "carousel slide"
        return kw

    def visit_strings(self, f):
        pass

    def html(self):
        indicators_content = []
        for i in xrange(len(self.container_info.slides)):
            active = ""
            if i==0 :
                active = "active"
            indicators_content.append(Tag('li', {'data-target': "#"+self.galleryid, "data-slide-to": i, "class": active}, content=""))
        indicators = Tag('ol', {'class': 'carousel-indicators'}, content=indicators_content)

        items = []
        slides = self.container_info.slides
        for i in xrange(len(slides)):
            imgcontent = []
            active = ""
            if(i==0):
                active = "active "
            imgcontent.append(Tag('img', {'src': slides[i].image}))
            imgcontent.append(Tag('div', {'class': 'carousel-caption'}, Tag('p', {}, slides[i].text)))
            items.append(Tag('div', {'class': active + "item"}, content=imgcontent))
        slides = Tag('div', {'class': 'carousel-inner'}, content=items)

        navPrev = Tag('a', {"class": "carousel-control left", "href": "#"+self.galleryid, "data-slide": "prev"}, content="&lsaquo;")
        navNext = Tag('a', {"class": "carousel-control right", "href": "#"+self.galleryid, "data-slide": "next"}, content="&rsaquo;")

        content = [indicators, slides, navPrev, navNext]
        tag = Tag('div', self.kwargs(), content=content)
        return tag


class Iterator(DictInited, Hooked):

    
    @property
    def hooks(self):
        if self.container_info.search is not None:
            hooks = ['find or add the needed search to the view']
        else:
            hooks = ['find or add the needed data to the view']
        hooks += ['resolve links href']
        return hooks

    class IteratorInfo(DictInited, Resolvable):

        """ Search Lists """
        class SearchQuery(DictInited):
            _schema = {
                "numberOfRows": {"_type": 0},
            }

        class Query(DictInited):

            class WhereClause(DictInited, Resolvable):
                _schema = {
                        "field_name": {"_type": ""},
                        "equal_to": {"_type": ""}
                }
                _resolve_attrs = (('field_name', 'field'),)
                _datalang_attrs = (('equal_to', 'equal_to_dl'),)

            _schema = {
                "sortAccordingTo": {"_type": ""},
                "numberOfRows": {"_type": 0},
                "where": {"_type": [], "_each": {"_type":WhereClause}}
            }

        class Row(DictInited):
            _schema = {
                "isListOrGrid": {"_type": ""},
                "layout": {"_type": Layout},
                "uielements": {"_type": [], "_each": {"_type": UIElement}},
            }

        _schema = {
            "entity": {"_type": ""},
            "query": {"_one_of": [{"_type" : Query}, {"_type": None}], "_default": None},
                # one or the other. validated in validate function.
            "search": {"_one_of": [{"_type" : SearchQuery}, {"_type": None}], "_default": None},

            "row": {"_type": Row}
        }

        _resolve_attrs = (("entity", "entity_resolved"),)

        def __init__(self, *args, **kwargs):
            super(Iterator.IteratorInfo, self).__init__(*args, **kwargs)

            if self.query is not None:
                for w in self.query.where:
                    w.field_name = encode_braces('tables/%s/fields/%s' % (self.entity, w.field_name))

        def validate(self):
            assert (self.query is None) != (self.search is None), "Can't tell whether search or query??? q: %r, s: %r" % (self.query, self.search)
            self.action = 'search' if self.search is not None else 'query'


    _schema = {
        "container_info": {"_type": IteratorInfo},
    }

    def visit_strings(self, f):
        for uie in self.container_info.row.uielements:
            uie.visit_strings(f)

    def html(self):
        inner_htmls = []

        def style_inner_uie(el, html):
            html.style_string += '; position: absolute; height: %dpx; width:%dpx; top: %dpx; left: %dpx; text-align:%s ' % (el.layout.height, el.layout.width, el.layout.top, el.layout.left, el.layout.alignment)
            return html

        for uie in self.container_info.row.uielements:
            uie_html = uie.html()
            uie_html = style_inner_uie(uie, uie_html)
            inner_htmls.append(uie_html)
        row_wrapper_style_string = 'display:block; position:relative; height:%dpx;' % (self.container_info.row.layout.height * 15)
        row_wrapper = Tag('div', {'style': row_wrapper_style_string}, content=inner_htmls)

        loop_contents = []
        loop_wrapper = Tag('div', {'style': 'position:relative;'}, content=loop_contents)
        loop_contents.append("{%% if %s %%}" % self._django_query_id)
        loop_contents.append("{%% for obj in %s %%}" % self._django_query_id)
        loop_contents.append(row_wrapper)
        loop_contents.append("{% endfor %}")
        loop_contents.append("{%% endif %%}")
        return loop_wrapper

