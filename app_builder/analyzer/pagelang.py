"Pagelang parsing and intermediate representation"

class PageLang(object):
    def __init__(self):
        pass

    def to_code(self):
        pass


def datalang_to_fields(tokens):
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

def parse_to_pagelang(pagelang_string, app):
    """
    http://google.com/
    https://gmail.com/
    internal://homepage/
    internal://Tweet_page/?Tweet=loop.Tweet& ... qstring 
    """

