from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm

# Create your models here.class UserForm(ModelForm):

# class User(models.Model):
#     username = models.CharField(label="Username", max_length=30, 
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'username'}))
#     email = models.CharField(label="Email", max_length=30, 
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'email'}))
#     password = models.CharField(label="Password", max_length=30, 
#                                widget=forms.TextInput(attrs={'class': 'form-control', 'name': 'password'}))
