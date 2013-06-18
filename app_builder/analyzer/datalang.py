"DataLang parsing and intermediate representation"

class DataLang(object):
    def __init__(self, context_type, seed_entity, fields):
        """
        context_type is Page, Loop, or _____
        field_list is a list of the fields which will be tacked on after seed
        """
        assert context_type in ['Page', 'Loop', 'Form', 'user']
        self.context_type = context_type
        self.seed_entity = seed_entity
        self.fields = fields

    def to_code(self, context=None, seed_id=None):
        if self.context_type == 'Form':
            seed_id = seed_id
        elif self.context_type == 'user':
            seed_id = 'request.user'
        else:
            seed_id = context.get_by_ref(self.seed_entity._django_model)

        def get_accessor(field):
            "This is separate function so we can have custom logic to handle users (get profile stuff)"
            return field._django_field_identifier
        return ''.join([seed_id] + ['.%s' % get_accessor(f) for f in self.fields])


def datalang_to_fields(starting_ent, tokens):
    field_entity_pairs = []
    current_ent = starting_ent
    obj_type = 'object'
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
                    obj_type = 'object'
            else:
                assert last_item_in_loop, "You can't chain things on after a primval"
                field_entity_pairs.append((f, None))
                obj_type = 'primval'
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
                    obj_type = 'collection'
                else:
                    assert f.type == 'o2o', "Many to many is not yet supported"
                    if last_item_in_loop:
                        obj_type = 'object'
            except IndexError:
                raise Exception("Couldn't find field with the name or related name: %r" % tok)

    return field_entity_pairs

def parse_to_datalang(datalang_string, app):
    tokens = datalang_string.split('.')
    # 1. get the seed type to start the chaining in step 2
    if tokens[0] == 'CurrentUser':
        context_type = 'user'
        ent = filter(lambda e: e.is_user, app.tables)[0]
        tokens = tokens[1:]

    elif tokens[0] == 'Page' or tokens[0] == 'loop':
        context_type = tokens[0].lower()
        ent = app.tables[0].app.find('tables/%s' % tokens[1], name_allowed=True)
        tokens = tokens[2:]

    elif tokens[0] == 'this': # for forms
        context_type = 'form'
        #ent = this_entity.ref
        ent = None # TODO FIXME get the entity for this form
        tokens = tokens[1:]

    else:
        raise Exception("Not Yet Implemented: %r" % tokens[0])

    # 2. get the list of fields by performing entity-field-entity chaining
    field_entity_pairs = datalang_to_fields(ent, tokens)
    # 3. create a datalang instance and bind it to dest_attr
    dl = DataLang(context_type, ent, [ f for f, e in field_entity_pairs ])
    return dl


