from datalang import parse_to_datalang
"""
    Pagelang parsing and intermediate representation.
    Used to validate and convert link strings to renderable objects.
    This is done via either rendering the objects in python code (using reverse)
    or in template code (using url tag)
"""

class PageLang(object):
    def __init__(self, page_str, app, page_name=None, datalangs=None, external=False):
        self.data_langs = datalangs
        self.page_str = page_str
        self.is_external = external
        self.page_name = page_name
        if self.is_external:
            # Since this is an external link, we set page to None
            self.page = None
        else:
            self.page = app.find("pages/%s" % page_name, name_allowed=True)

    def to_code(self,context=None, template=False):
        """ If template is false reverse is used. Otherwise we use the url tag """
        if not template:
            return "{%% url webapp.pages.%s %%}" % self.page._django_view.identifier
        else:
            assert False, "Non templates are not yet implemented"

def parse_to_pagelang(pagelang_string, app):
    """
    Parses pagelang strings of these types:
    http://google.com/
    https://gmail.com/
    internal://homepage/ (no datalang)
    internal://Tweet_page/?Tweet=loop.Tweet& ... qstring (datalang)
    """

    def get_page_name(pagelang_string):
        if "internal://" not in pagelang_string:
            return None
        else:
            pagelang_str = pagelang_string[len("internal://"):]
            if '/' in pagelang_str:
                return pagelang_str[:pagelang_str.index('/')]
            else:
                return pagelang_str

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
                datalangs[k] = parse_to_datalang(v, app)
            return datalangs
        
    if not pagelang_string.startswith("internal://"):
        assert pagelang_string.startswith("http://") or pagelang_string.startswith("https://"), "Not a valid link bro: %r" % pagelang_string
        return PageLang(pagelang_string, app, external=True)
    else:
        page_name = get_page_name(pagelang_string)
        datalang_str = pagelang_string[len("internal://"):]
        return PageLang(pagelang_string, app, page_name=page_name, datalangs=get_datalangs(datalang_str))
