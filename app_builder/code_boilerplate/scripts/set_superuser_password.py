import os, os.path
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'settings.prod')
sys_list = sys.path
app_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..')
sys_list.insert(0, app_dir)

from webapp.models import User

admin_user = User.objects.get(username='admin')
admin_user.set_password("password")
admin_user.save()
