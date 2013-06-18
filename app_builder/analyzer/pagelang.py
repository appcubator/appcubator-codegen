"""
    Pagelang parsing and intermediate representation.
    Used to validate and convert link strings to renderable objects.
    This is done via either rendering the objects in python code (using reverse)
    or in template code (using url tag)
"""

"""To code:
In: context maybe
Out: template code, or python reverse code
If template, use url tag. if python use reverse.
Get the view function name, resolve datalangs w the context.
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

    def to_code(self):
        # Create datalangs here for query string params such as (tweet=Loop.Tweet)
        pass


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
            return pagelang_str[:pagelang_str.index('/')]

    def get_datalangs(pagelang_str):
        datalang_str = pagelang_str[pagelang_str.split('/')+1:]
        datalangs = []
        if len(datalang_str) == 0:
            # Case where we have no datalangs
            return datalangs
        else:
            datalang_str = datalang_str[1:] # Get rid of qn mark
            for kv in datalang_str.split('&'):
                (k, v) = kv.split('=')
                datalangs.append((k, v))
            return datalangs
        
    if "internal://" not in pagelang_string:
        return PageLang(pagelang_string, app, external=True)
    else:
        page_name = get_page_name(pagelang_string)
        datalang_str = pagelang_string[len("internal://"):]
        return PageLang(pagelang_string, app, page_name=page_name, datalangs=get_datalangs(datalang_str))
