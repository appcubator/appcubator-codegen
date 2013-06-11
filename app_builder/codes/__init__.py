from jinja2 import Environment, FileSystemLoader, StrictUndefined
import os.path

env = Environment(trim_blocks=True, lstrip_blocks=True, loader=FileSystemLoader(
    os.path.join(os.path.dirname(__file__), 'code_templates')), undefined=StrictUndefined)

from models import *
from views import *
from forms import *
from urls import *
from tests import *
from imports import *
from templates import *
