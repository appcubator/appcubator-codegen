#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.prod")

    from django.core.management import call_command

    call_command('test', 'webapp')
