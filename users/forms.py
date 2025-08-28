from django import forms
from parler.forms import TranslatableModelForm
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordResetForm,
    SetPasswordForm,
)
from django.contrib.auth import authenticate

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=False, max_length=30)
    last_name = forms.CharField(required=False, max_length=30)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@example.com'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply consistent styling
        for name, field in self.fields.items():
            if name not in self.Meta.widgets:  # email already styled
                base_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = (base_class + ' form-control').strip()
            # Force placeholders (assign directly so they always show)
            if name == 'first_name':
                field.widget.attrs['placeholder'] = 'First name'
            elif name == 'last_name':
                field.widget.attrs['placeholder'] = 'Last name'
        # Password fields provided by UserCreationForm
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name")
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'you@example.com'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    remember = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={
        'class': 'custom-control-input'
    }))

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password")
            cleaned["user"] = user
        return cleaned


class StyledPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'you@example.com'
        })


class StyledSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in ['new_password1', 'new_password2']:
            self.fields[name].widget.attrs.update({
                'class': 'form-control',
                'placeholder': 'New password' if name == 'new_password1' else 'Confirm new password'
            })
