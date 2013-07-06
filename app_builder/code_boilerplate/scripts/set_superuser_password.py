#!/usr/bin/python
# ONLY RUN FROM THE ROOT DIRECTORY OF THE APP
import os, os.path
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

app_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
os.environ['PATH'] = app_dir + ":" + os.environ['PATH']

from webapp.models import User

admin_user = User.objects.get(username='admin')
admin_user.set_password("password")
admin_user.save()
