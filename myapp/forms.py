from django import forms
from .models import Art, Contact

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'username',
            'placeholder': 'you@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'id': 'password',
            'placeholder': 'Enter your password'
        })
    )
loginForm = LoginForm

class ArtForm(forms.ModelForm):
    class Meta:
        model = Art
        fields = ['name', 'lastname', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your first name',
                'required': True
            }),
            'lastname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your last name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'name@example.com',
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your architectural project or inquiry...',
                'rows': 4,
                'required': True
            }),
        }

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['phone']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter phone number (e.g. +91 9876543210)',
                'required': True
            })
        }
