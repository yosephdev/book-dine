from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.core.validators import RegexValidator
from django.db import models
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):    
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        required=False
    )
    

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + \
            ('phone_number', 'date_of_birth')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password1', css_class='form-control'),
            Field('password2', css_class='form-control'),
            Field('phone_number', css_class='form-control'),
            Field('date_of_birth', css_class='form-control'),
        )


class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(
        max_length=15,
        validators=[RegexValidator(
            r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')],
        required=False
    )

    class Meta(UserChangeForm.Meta):
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('email', css_class='form-control'),
            Field('phone_number', css_class='form-control'),
            Field('date_of_birth', css_class='form-control'),
            Field('profile_picture', css_class='form-control'),
        )
