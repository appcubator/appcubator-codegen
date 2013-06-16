from dict_inited import DictInited
from utils import encode_braces, decode_braces


class DataLang(object):
    def __init__(self, context_type, seed_entity, fields):
        """
        context_type is Page, Loop, or _____
        field_list is a list of the fields which will be tacked on after seed
        """
        assert context_type in ['Page', 'Loop', 'Form', 'user']
        self.context_type = context_type
        self.seed_entity = seed_entity
        self.chain_of_renderable = chain_of_renderable

    def to_code(self, context=None, seed_id=None):
        if self.context_type == 'Form':
            seed_id = seed_id
        elif self.context_type == 'user':
            seed_id = 'request.user'
        else:
            seed_id = context.get_by_ref(self.seed_entity)

        def get_accessor(field):
            "This is separate function so we can have custom logic to handle users (get profile stuff)"
            return field._django_field.identifier
        return ''.join([seed_id] + ['.%s' % get_accessor(f) for f in fields])


def datalang_to_fields(self, starting_ent, tokens):
    field_entity_pairs = []
    current_ent = starting_ent
    for idx, tok in enumerate(tokens):
        last_item_in_loop = (idx == len(tokens) - 1)

        field_candidates = [ f for f in current_ent.fields if f.name == tok ]
        assert len(field_candidates) <= 1, "Found more than one field with the name: %r" % tok
        # try to get the field with this name on this entity
        try:
            f = field_candidates[0]
            if f.is_relational():
                current_ent = f._django_field.rel_model_id.ref._entity
                field_entity_pairs.append((f, current_ent))
                if last_item_in_loop:
                    return (field_entity_pairs, 'object')
            else:
                assert last_item_in_loop, "You can't chain things on after a primval"
                field_entity_pairs.append((f, None))
                return (field_entity_pairs, 'singular')
        # try to get the field with this related_name on this entity
        except IndexError:
            # it couldn't find a field with this name, so let's try to find a related name.
            field_candidates = [ f for path, f in current_ent.app.search(r'^tables/\d+/fields/\d+$') if f.is_relational() and f.related_name == tok and f.entity == current_ent]
            assert len(field_candidates) <= 1, "Found more than one field with the related name: %r and the entity: %r" % (tok, current_ent.name)
            try:
                f = field_candidates[0]
                current_ent = f._django_field.model._entity
                field_entity_pairs.append((f, current_ent))
                if f.type == 'fk':
                    assert last_item_in_loop, "You can't chain things on after collection"
                    return (field_entity_pairs, 'collection')
                else:
                    assert f.type == 'o2o', "Many to many is not yet supported"
                    if last_item_in_loop:
                        return (field_entity_pairs, 'singular')
            except IndexError:
                raise Exception("Couldn't find field with the name or related name: %r" % tok)



class Resolvable(object):

    """
    Mixin allowing you to specify attributes you want to resolve.
    See _resolve_attrs in LinkLang for example.
    """

    def resolve(self):
        assert hasattr(self, 'app'), "You must have something at attribute \"app\""
        for src_attr, dest_attr in self.__class__._resolve_attrs:
            path_string = decode_braces(getattr(self, src_attr))
            setattr(self, dest_attr,  self.app.find(
                path_string, name_allowed=True))

    def resolve_data(self):
        assert hasattr(self, 'app'), "You must have something at attribute \"app\""
        for src_attr, dest_attr in self.__class__._resolve_attrs:
            linklang_string = getattr(self, src_attr)

            # 1. get the seed type to start the chaining in step 2
            # 2. get the list of fields by performing entity-field-entity chaining
            # 3. create a datalang instance and bind it to dest_attr


# 4. later on in code generation, the datalang will be converted to code
#      by providing a page and loop context and hoping for the best.





    """



# datalang is going to be an ORM-like query language.:
page.Tweet.content.whatever blah blah
CurrentUser.First Name
Student.grades
Student.grades?number=50








# new link lang is going to be:
internal://<page name>/?<urldata type>=<datalang> & so on.
its equivalent to:

    {
        page_name: ""    # resolvable to page
      , urldata: {
            <entity name>: <datalang>    # key is resolvable to entity, value is resolvable to some datalang
        }
    }










# this is the old crappy linklang
class LinkLang(DictInited, Resolvable):
    _schema = {
        "page_name": {"_type": ""},
        "urldata": {"_type": {}},
        # "page": { "_type": Page"} # DO NOT UNCOMMENT. this gets added after resolve.
    }

    _resolve_attrs = (('page_name', 'page'),)


class EntityLang(DictInited, Resolvable):
    _schema = {"entity_name": {"_type": ""}}
    _resolve_attrs = (('entity_name', 'entity'),)

"""
