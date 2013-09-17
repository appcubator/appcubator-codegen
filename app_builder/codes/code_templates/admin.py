from django.utils.translation import ugettext, ugettext_lazy as
class MyUserAdmin(UserAdmin):
    """
    Overrides UserAdmin to accomodate our custom User Model,
    which takes email, name, and password.
    """

    # use this to render the form on the admin panel
    add_form_template = "admin/auth/add_user.html"

    # use this to validate, and process the form.
    add_form = AdminUserCreateForm

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'username')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'name')}
        ),
    )
