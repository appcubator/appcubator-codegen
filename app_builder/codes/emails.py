from app_builder import naming
from . import env

class Emailer(object):

    def __init__(self, identifier, api_key):
        """
            Renders the emailer module that lets the generated app to send emails via us.
        """
        self.identifier = identifier
        self.api_key = api_key
        self.code_path = "webapp/emailer.py"

        self.locals = {}
        self.namespace = naming.Namespace(parent_namespace=self.identifier.ns)
        self.locals['api_key'] = api_key

    def render(self):
        return env.get_template('emailer.py.template').render(view=self, imports=self.namespace.imports(), locals=self.locals)
