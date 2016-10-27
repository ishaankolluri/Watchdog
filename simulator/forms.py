from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm


# If you don't do this you cannot use Bootstrap CSS
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
    password = forms.CharField(label="Password", max_length=30, 
                               widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))


class UserForm(ModelForm):
	username = forms.CharField(label="Username", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
	email = forms.CharField(label="Email", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'email'}))
	password = forms.CharField(label="Password", max_length=30, widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
	
	class Meta:
		model = User
		fields = ('username', 'email', 'password')
