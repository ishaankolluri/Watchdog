from django.contrib.auth.models import User
from django.shortcuts import render

from simulator.forms import UserForm
from simulator.models import Instrument, Position


def home(request):
    return render(request, 'home.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            user.save()
            return render(request, 'home.html')
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form':form})


def signedup(request):
    return render(request, 'signedup.html')


def profile(request):
    # How do I access the user data in the request?
    print request.POST
    return render(request, 'profile.html')
