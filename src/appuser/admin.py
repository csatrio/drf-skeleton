from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm, UserCreationForm as BaseUserCreationForm

from .models import User


class UserCreationForm(BaseUserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')


class UserChangeForm(BaseUserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email')


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['username', 'email']
    pass


# register UserAdmin
admin.site.register(User, UserAdmin)
