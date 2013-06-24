from dict_inited import DictInited
from resolving import Resolvable
from utils import encode_braces, decode_braces
from copy import deepcopy

from app_builder.htmlgen import Tag

from . import env
from . import logger

def get_uielement_by_type(type_string):
    UIELEMENT_TYPE_MAP = {'form': Form,
                          'loop': Iterator,
                          'node': Node,
                          'thirdpartylogin' : ThirdPartyLogin
                         }
    subclass = UIELEMENT_TYPE_MAP[type_string]
    return subclass


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
                   )

        elif action == 'signup':
            return ('create signup form if not exists',
                    'import form into form receivers',
                    'create signup form receiver if not exists',
                    'create url for form receiver',
                   )

        else:
            assert False, "Form action not recognized: %s" % action



    class FormInfo(DictInited):

        class FormInfoInfo(DictInited, Resolvable):

            class FormField(object):

                def htmls(field):
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

                    elif field.displayType == 'button':
                        base_attribs['type'] = 'submit'
                        base_attribs['value'] = field.placeholder
                        base_attribs['class'] = 'btn'


                    # create the html
                    field_html = Tag(tagname, base_attribs, content=content)
                    if field.displayType == 'email-text':
                        decorating_wrapper = Tag('div', {'class': 'input-prepend'}, content=(
                                Tag('span', {'class':'add-on'}, content="@"),
                                field_html))
                        field_html = decorating_wrapper

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
                    "placeholder": {"_type": ""},
                    "label": {"_type": ""},
                    "displayType": {"_type": ""},
                    "options": {"_type": [], "_default": [], "_each": {"_type": ""}}  # XXX what is this, in more detail?
                }

                _resolve_attrs = (('field_name', 'model_field'),)

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.FormModelField, self).__init__(*args, **kwargs)
                    self.name = self.field_name
                    assert self.displayType != "button", "If this is a button, please remove the displayType, or the name, or options."

                def set_backend_name(self):
                    self.backend_field_name = self.model_field._django_field_identifier

            class FormNormalField(FormField, DictInited):
                _schema = {
                    "name": {"_type": ""},
                    "placeholder": {"_type": ""},
                    "label": {"_type": ""},
                    "displayType": {"_type": ""},
                    "options": {"_type": [], "_each": {"_type": ""}}  # XXX what is this, in more detail?
                }

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.FormNormalField, self).__init__(*args, **kwargs)
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

            class RelationalAction(DictInited):
                _schema = {
                    "set_fk": {"_type": ""},
                    "to_object": {"_type": ""}
                }
                # in the strings, "this" will refer to the instance of the entity being created in the form
                # set fk could be something like, "this.teacher" or "CurrentUser.mygroup".
                # to object could be something like, "Page.Teacher" or "Page.Group"

            class RoleRouting(DictInited, Resolvable):
                _schema = {
                    "role": {"_type": ""}, # name of the user role (Student)
                    "redirect": {"_type": ""} # link lang it should redirect to
                }
                _resolve_attrs = ()
                _pagelang_attrs = (('redirect', 'goto_pl'),)

                def __init__(self, *args, **kwargs):
                    super(Form.FormInfo.FormInfoInfo.RoleRouting, self).__init__(*args, **kwargs)

                def validate(self):
                    assert self.role in [u.name for u in self.app.users], "Role not recognized."

            _schema = {
                "entity": {"_type": ""},
                "action": {"_type": ""},
                "fields": {"_type": [], "_each": {"_one_of": [{"_type": FormModelField},{"_type": FormNormalField},{"_type": ButtonField}]}},
                "actions": {"_type": [], "_default": [], "_each": {"_type": RelationalAction}},
                "goto" : {"_one_of": [{"_type" : ""}, {"_type": None}]},
                "loginRoutes": {"_one_of": [{"_type" : [], "_each": {"_type": RoleRouting}}, {"_type": None}], "_default": None},
                "signupRole" : {"_one_of": [{"_type" : ""}, {"_type": None}], "_default": None},

            }

            _resolve_attrs = (('entity', 'entity_resolved'),)
            # overridden resolve_page function => goto_pl will only exist if redirect = True. see the code for that fn.
            _pagelang_attrs = (('goto', 'goto_pl'), )

            def __init__(self, *args, **kwargs):
                super(Form.FormInfo.FormInfoInfo, self).__init__(*args, **kwargs)
                for f in filter(lambda x: isinstance(x, Form.FormInfo.FormInfoInfo.FormModelField), self.fields):
                    f.field_name = encode_braces('tables/%s/fields/%s' % (self.entity, f.field_name))

            def validate(self):
                if self.action == 'login' and self.app.multiple_users:
                    assert self.loginRoutes is not None, "login form must have loginRoutes"

                if self.action == 'signup' and self.app.multiple_users:
                    assert self.signupRole is not None, "signup form must have signupRole"
                    assert self.signupRole in [u.name for u in self.app.users]

            def resolve_page(self):
                if self.goto is None:
                    self.redirect = False
                else:
                    self.redirect = True
                    super(Form.FormInfo.FormInfoInfo, self).resolve_page()

            def get_actions_as_tuples(self):
                return [(a.set_fk, a.to_object) for a in self.actions]

            def string_ref_to_inst_only(self, s):
                if s.startswith('Page') or s.startswith('Loop'):
                    return ''.join(s.split('.')[:2])
                return s.split('.')[0]


            def get_needed_page_entities(self):
                # collect all refs in actions
                data_refs = ( item for tup in self.get_actions_as_tuples() for item in tup )
                entities = []

                for ref in data_refs:
                    toks = ref.split('.')
                    if toks[0] == 'Page':
                        name_of_type_of_inst_needed_from_page = toks[1]
                        entity = self.app.find('entities/%s' % name_of_type_of_inst_needed_from_page, name_allowed=True)
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
        "Translator: This is a form, nothing to do."
        pass

    def set_post_url(self, url):
        self.post_url = url

    def html(self):
        fields = ['{% csrf_token %}']
        for f in self.container_info.form.fields:
            # put the django model name in.
            f.set_backend_name()
            fields.extend(f.htmls())
        fields.append(Tag('div', {'class': 'form-error field-all'}))
        try:
            post_url = self.post_url
        except AttributeError:
            post_url = "ASDFJKWTF"
        attribs = {'method': 'POST',
                   'action': post_url,
                   'class': self.class_name}
        form = Tag('form', attribs, content=fields)
        return form

class ThirdPartyLogin(DictInited, Hooked, Resolvable):
    """ Represents all third party logins: [linkedin, facebook, twitter]"""

    _schema = {
        "provider": {"_type" : ""},
        "content" : {"_type" : ""},
        "goto" : {"_type" : ""}
    }

    _resolve_attrs = ()
    _pagelang_attrs = (('goto', 'goto_pl'), )

    def __init__(self, *args, **kwargs):
        super(ThirdPartyLogin, self).__init__(*args, **kwargs)

    def resolve_page(self):
        if self.goto is None:
            self.redirect = False
        else:
            self.redirect = True
            super(ThirdPartyLogin, self).resolve_page()

    def html(self):
        tpl_template = env.get_template('thirdpartylogin.html')
        tpl = Tag('div', {}, content=tpl_template.render(context=self))
        return tpl

    def visit_strings(self, f):
        pass


class Node(DictInited, Hooked):  # a uielement with no container_info
    _hooks = ['resolve links href']

    _schema = {
        "content": {"_default": None, "_one_of": [{"_type": None}, {"_type": "", "_default": ""}]},  # TODO may have reference
        # "isSingle": { "_type" : True }, # don't need this because it's implied from tagname
        "content_attribs": {"_type": {}},  # TODO may have reference
        "class_name": {"_type": ""},
        "tagName": {"_type": ""},
    }

    def __init__(self, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        if self.content is None:
            self.content = ""

    def kwargs(self):
        kw = {}
        kw = deepcopy(self.content_attribs)
        kw['class'] = 'node ' + self.class_name
        return kw

    def visit_strings(self, f):
        # Resolves either images or URLs
        self.content = f(self.content)
        try:
            self.content_attribs['src'] = f(self.content_attribs['src'])
        except KeyError:
            pass
        try:
           self.content_attribs['href'] = f(self.content_attribs['href'])
        except KeyError:
            pass


    def html(self):
        try:
            content = self.content()
        except TypeError:
            content = self.content
        tag = Tag(self.tagName, self.kwargs(), content=content)
        return tag


class Iterator(DictInited, Hooked):

    _hooks = ['find or add the needed data to the view']

    class IteratorInfo(DictInited, Resolvable):

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
            "entity": {"_type": ""},  # TODO may have reference
            "action": {"_type": ""},
            "query": {"_type": Query},
            "row": {"_type": Row}
        }

        _resolve_attrs = (("entity", "entity_resolved"),)

        def __init__(self, *args, **kwargs):
            super(Iterator.IteratorInfo, self).__init__(*args, **kwargs)
            for w in self.query.where:
                w.field_name = encode_braces('tables/%s/fields/%s' % (self.entity, w.field_name))

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
        loop_contents.append("{%% for obj in %s %%}" % self._django_query_id)
        loop_contents.append(row_wrapper)
        loop_contents.append("{% endfor %}")
        return loop_wrapper

