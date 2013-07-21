"""
from app_builder.controller import create_codes
from app_builder.coder import Coder, write_to_fs
from app_builder.tests.app_state_interface import AppStateTestInterface
from app_builder.app_manager import AppManager
"""

from app_builder.analyzer import App, InvalidDict
import unittest
import os, os.path


if __name__ == "__main__":
    T = unittest.TestLoader()
    suite = T.discover('app_builder.tests.functional_states', pattern='*.py',
            top_level_dir=os.path.join(os.path.abspath(os.path.dirname(__file__)),'..'))
    unittest.TextTestRunner(verbosity=2).run(suite)
