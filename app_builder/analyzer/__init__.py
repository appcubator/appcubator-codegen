


from jinja2 import Environment, FileSystemLoader

env = Environment(trim_blocks=True, lstrip_blocks=True, loader=FileSystemLoader(
    'templates'))

from analyzer import *
