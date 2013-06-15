# -*- coding: utf-8 -*-

import os
import os.path
import re
import logging


from dict_inited import DictInited
from utils import encode_braces, decode_braces
from resolving import Resolvable, LinkLang, EntityLang

from . import env

logger = logging.getLogger("codegen-analyzer")

# tables

class EntityField(DictInited):
    _schema = {
        "name": {"_type": ""},
        "type": {"_type": ""}
    }

    def is_relational(self):
        return False


class EntityRelatedField(DictInited, Resolvable):
    _schema = {
        "name": {"_type": ""},
        "type": {"_type":""}, # one to one, many to one, many to many
        "entity_name": {"_type" : ""},
        'related_name': {"_type": ""}
    }
    _resolve_attrs = (('entity_name', 'entity'),)

    def is_relational(self): 
        return True

    def __init__(self, *args, **kwargs):
        super(EntityRelatedField, self).__init__(*args, **kwargs)
        self.entity_name = encode_braces('tables/%s' % self.entity_name)


class Entity(DictInited):
    _schema = {
        "name": {"_type": ""},
        "fields": {"_type": [], "_each": {"_one_of":[{"_type": EntityRelatedField}, {"_type": EntityField}]}},
    }

    def __init__(self, *args, **kwargs):
        super(Entity, self).__init__(*args, **kwargs)
        self.is_user = False

    def relational_fields(self):
        return filter(lambda x: x.is_relational(), self.fields)


class UserRole(DictInited):
    _schema = {
        #"name": {"_type":""}, # TODO
        "fields": {
            "_type": [],
            "_each": {"_one_of":[{"_type": EntityRelatedField}, {"_type": EntityField}]}
        }
    }


# Pages

class Navbar(DictInited):

    class NavbarItem(DictInited):
        _schema = {
            "url": {"_type": ""},
            "title": { "_type": "" }
        }

    _schema = {
        "brandName": {"_one_of": [{"_type": ""}, {"_type": None}]},
        "isHidden": {"_type": True},
        "links": {"_type": [], "_each": {"_type": NavbarItem}}
    }

    def render(self):
        if self.brandName is None:
            self.brandName = self.app.name
        return env.get_template('navbar.html').render(navbar=self)

class Footer(DictInited):

    class FooterItem(DictInited):
        _schema = {
            "url": {"_type": ""},
            "title": { "_type": "" }
        }

    _schema = {
        "customText": {"_type": ""},
        "isHidden": {"_type": True},
        "links": {"_type": [], "_each": {"_type": FooterItem}}
    }

from uielements import UIElement

class Page(DictInited):

    class URL(DictInited):

        _schema = {
            "urlparts": {"_type": [], "_each": {"_one_of": [{"_type": ""}, {"_type": EntityLang}]}}
        }

        def is_valid(self):
            for u in self.urlparts:
                try:
                    if not re.match(r'^[a-zA-Z0-9-_]+$', u):
                        logger.error("Page URL %s is not valid." % u)
                        return False
                except TypeError:
                    logger.error("Page URL %s encountered TypeError" % u)
            return True


    _schema = {
        "name": {"_type": ""},
        "url": {"_type": URL},
        "navbar": {"_type": Navbar},
        "footer": {"_type": Footer},
        "uielements": {"_type": [], "_each": {"_type": UIElement}},
        "access_level": {"_type": ""}
    }

    @property
    def url_regex(page):
        url_regex = "r'^"
        for x in page.url.urlparts:
            if isinstance(x, basestring):
                url_regex += x + '/'
            else:
                url_regex += r'(\d+)/'
        url_regex += "$'"
        return url_regex

    def is_static(self):
        # returns true iff there are no tables in the url parts
        return len(filter(lambda x: isinstance(x, EntityLang), self.url.urlparts)) == 0

    def get_tables_from_url(self):
        return [l.entity for l in filter(lambda x: isinstance(x, EntityLang), self.url.urlparts)]


class Email(DictInited):
    _schema = {
        "name": {"_type": ""},
        "subject": {"_type": ""},
        "content": {"_type": ""},
    }

# Put it all together, you get an App

from uielements import Form, Iterator

class App(DictInited):
    _schema = {
        "name": {"_type": "", "_minlength": 2, "_maxlength": 255},
        "info": {"_type": {}, "_mapping": {
            "description": {"_type": ""},
            "keywords": {"_type": ""},
        }},
        "users": {"_type": [], "_each": {"_type": UserRole}},
        "tables": {"_type": [], "_each": {"_type": Entity}},
        "pages": {"_type": [], "_each": {"_type": Page}},
        "emails": {"_type": [], "_each": {"_type": Email}},
    }

    @classmethod
    def create_from_dict(cls, data, *args, **kwargs):
        # preprocess data
        self = super(App, cls).create_from_dict(data, *args, **kwargs)

        for p in self.pages:
            assert p.url.is_valid(), "Url not valid: %r" % p.url.urlparts

        # create the user entity based on userconfig
        userdict = {
            "name": "User",
            "fields": [
                {
                    "name": "username",
                    "type": "text",
                },
                {
                    "name": "First Name",
                    "type": "text",
                },
                {
                    "name": "Last Name",
                    "type": "text",
                },
                {
                    "name": "Email",
                    "type": "text",
                },
            ]
        }
        userentity = Entity.create_from_dict(userdict)
        userentity.user_fields = [f for f in userentity.fields] # create a new list, bc the old one is mutated later

        # combine all the fields from all the user roles
        combined_fields_from_all_roles = []
        for u in self.users:
            combined_fields_from_all_roles.extend(u.fields)

        # deduplicate by name to get the total set of fields that the userprofile will have.
        user_profile_field_set = []
        for field in combined_fields_from_all_roles:
            for already_added_field in user_profile_field_set]:
                if field.name != already_added_field.name:
                    user_profile_field_set.append(field)
                else:
                    assert field.type == already_added_field.type, "Two user role fields had same name but different type."

        userentity.user_profile_fields = user_profile_field_set

        userentity.fields = userentity.user_fields + userentity.user_profile_fields

        userentity.is_user = True
        userentity.role_names = [ u.name for u in self.users ]

        self.tables.append(userentity)
        self.userentity = userentity # just binding for convenience

        # HACK replace uielements with their subclass
        for p in self.pages:
            uies = []
            for uie in p.uielements:
                subclass = uie.subclass
                subclass._path = uie._path
                uies.append(subclass)
            p.uielements = uies

        for path, row in self.search(r'pages/\d+/uielements/\d+/container_info/row$'):
            uies = []
            for uie in row.uielements:
                subclass = uie.subclass
                subclass._path = uie._path
                uies.append(subclass)
            row.uielements = uies


        # HACK give everything a reference to the app
        for path, obj in filter(lambda u: isinstance(u[1], DictInited), self.iternodes()):
            obj.app = self

        # Fix reflang namespaces
        for path, fii in filter(lambda n: isinstance(n[1], Form.FormInfo.FormInfoInfo), self.iternodes()):
            if fii.belongsTo is not None:
                fii.belongsTo = encode_braces('tables/%s' % fii.belongsTo)
            fii.entity = encode_braces('tables/%s' % fii.entity)

        for path, ll in filter(lambda n: isinstance(n[1], LinkLang), self.iternodes()):
            ll.page_name = encode_braces('pages/%s' % ll.page_name)

        for path, el in filter(lambda n: isinstance(n[1], EntityLang), self.iternodes()):
            el.entity_name = encode_braces('tables/%s' % el.entity_name)

        for path, ii in filter(lambda n: isinstance(n[1], Iterator.IteratorInfo), self.iternodes()):
            ii.entity = encode_braces(
                'tables/%s' % ii.entity)  # "Posts" => "tables/Posts"

        # Resolve reflangs
        for path, rl in filter(lambda n: isinstance(n[1], Resolvable), self.iternodes()):
            rl.resolve()


        return self
