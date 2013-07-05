#!/usr/bin/python
from webapp.models import User

admin_user = User.objects.get(username='admin')
admin_user.set_password("password")
admin_user.save()
