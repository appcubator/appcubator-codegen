from datalang import parse_to_datalang
import re

"""
    Pagelang parsing and intermediate representation.
    Used to validate and convert link strings to renderable objects.
    This is done via either rendering the objects in python code (using reverse)
    or in template code (using url tag)
"""

class PageLang(object):
    def __init__(self, page_str, app, page_name=None, entity_datalang_map=None, external=False):
        """datalangs is a map from entity to it's datalang in the pagelang. it must be in the context of the target page"""
        self.entity_datalang_map = entity_datalang_map
        self.page_str = page_str
        self.is_external = external
        self.page_name = page_name
        if self.is_external:
            # Since this is an external link, we set page to None
            self.page = None
            assert self.entity_datalang_map is None, "External link, don't pass datalangs to this."
        else:
            self.page = app.find("pages/%s" % page_name, name_allowed=True)

            # check that the data on the page matches the data in this pagelang.
            entities_on_page = self.page.get_tables_from_url()
            assert len(entities_on_page) == len(self.entity_datalang_map), "Number of datalangs to page don't even match."
            for e in entities_on_page:
                assert e in self.entity_datalang_map, "Entity %r in page context but not found in pagelang's datalangs." % e.name

    def to_code(self,context=None, template=False):
        """ If template is false reverse is used. Otherwise we use the url tag """
        if not template:
            datalang_variable_string = ''.join(['%s ' % self.entity_datalang_map[e].to_code() for e in self.page.get_tables_from_url()])
            return "{%% url webapp.pages.%s %s%%}" % (self.page._django_view.identifier, datalang_variable_string)
        else:
            assert False, "Non templates are not yet implemented"

def parse_lang(pagelang_string):
    """Given a string, try to parse out the page name and k, v pairs of the querystring after it."""
    m = re.match(r'^internal:\/\/([^\/]+)\/?(\?[^&=\/]+=[^&=\/]+(&[^&=\/]+=[^&=\/]+)+?)?$', pagelang_string)
    assert m is not None, "Invalid pagelang: %r" % pagelang_string
    page_name = m.group(1)

    # remove ?mark from beginning, then split on ampersand, then on equal sign.
    # ?a=b&c=d => [(a,b),(c,d)]
    if m.group(2) is None:
        qs_params = []
    else:
        qs_params = [ (x.split('=')[0], x.split('=')[1]) for x in m.group(2)[1:].split('&') ]

    return page_name, qs_params


def parse_to_pagelang(pagelang_string, app):
    """
    Parses pagelang strings of these types:
    http://google.com/
    https://gmail.com/
    internal://homepage/ (no datalang)
    internal://Tweet_page/?Tweet=loop.Tweet& ... qstring (datalang)
    """

    def get_datalangs(pagelang_str):
        """ Returns a dictionary of datalang objects referenced by their keys """
        datalangs = {}
        if '/' not in pagelang_str:
            return datalangs

        datalang_str = pagelang_str[pagelang_str.index('/')+1:]
        if len(datalang_str) == 0:
            # Case where we have no datalangs
            return datalangs
        else:
            datalang_str = datalang_str[1:] # Get rid of qn mark
            for kv in datalang_str.split('&'):
                (k, v) = kv.split('=')
            return datalangs

    if not pagelang_string.startswith("internal://"):
        assert pagelang_string.startswith("http://") or pagelang_string.startswith("https://"), "Not a valid link bro: %r" % pagelang_string
        return PageLang(pagelang_string, app, external=True)
    else:
        page_name, datalang_data = parse_lang(pagelang_string)

        entity_datalang_map = {}
        for entity_name, datalang_str in datalang_data:
            entity = app.find('tables/%s' % entity_name, name_allowed=True)
            entity_datalang_map[entity] = parse_to_datalang(datalang_str, app)


        return PageLang(pagelang_string, app, page_name=page_name, entity_datalang_map=entity_datalang_map)
