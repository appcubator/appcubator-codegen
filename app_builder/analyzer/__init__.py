


from jinja2 import Environment, FileSystemLoader
import os.path

env = Environment(trim_blocks=True, lstrip_blocks=True, loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'templates')))

from analyzer import *
