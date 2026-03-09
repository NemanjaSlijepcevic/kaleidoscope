from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User, Group


class UserGroupsForm(forms.ModelForm):
    group_map = {
        'add': 'Add',
        'edit': 'Edit',
        'delete': 'Delete',
    }

    add = forms.BooleanField(required=False, label=_("Can Add"))
    edit = forms.BooleanField(required=False, label=_("Can Edit"))
    delete = forms.BooleanField(required=False, label=_("Can Delete"))

    def __init__(self, *args, **kwargs):
        self.is_superuser = kwargs.pop('is_superuser', False)
        user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if not self.is_superuser:
            # Remove group fields if not a superuser
            for field, group_name in self.group_map.items():
                self.fields.pop(field)

        elif user_instance:
            # Set initial values for group fields based on the user membership
            for field, group_name in self.group_map.items():
                self.fields[field].initial = self.instance.groups.filter(name=group_name).exists()

    def save(self, commit=True):
        user = super().save(commit=False)

        if commit or user.pk is None:
            user.save()

        # Assign user to groups based on form data
        if self.is_superuser:
            for field, group_name in self.group_map.items():
                group, created = Group.objects.get_or_create(name=group_name)
                if self.cleaned_data[field]:
                    user.groups.add(group)
                else:
                    user.groups.remove(group)

        return user


class SignupForm(UserCreationForm, UserGroupsForm):

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2',
        ]


class UserEditForm(UserChangeForm, UserGroupsForm):
    class Meta:
        model = User
        fields = [
            'username',
            'email'
        ]
