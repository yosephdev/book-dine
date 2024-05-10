from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for user registration. Inherits from Django's built-in UserCreationForm.
    Uses django-crispy-forms for better form rendering.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password1', css_class='form-control'),
            Field('password2', css_class='form-control'),
        )

class CustomAuthenticationForm(AuthenticationForm):
    """
    A custom form for user authentication. Inherits from Django's built-in AuthenticationForm.
    Uses django-crispy-forms for better form rendering.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('username', css_class='form-control'),
            Field('password', css_class='form-control'),
        )
