from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth.decorators import login_required
from simulator.forms import UserForm
from django.contrib.auth.models import User



# class LoginView(generic.TemplateView):
#     template_name = "login.html"

# @login_required(login_url="login/")
def home(request):
	return render(request, 'home.html')


def login(request):
	return render(request, 'login.html')

def signup(request):
    if request.method == "POST":

        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            login(user)
            # return HttpResponseRedirect('home.html')
            return render(request, 'home.html')
    else:
        form = UserForm()

    return render(request, 'signup.html', {'form':form})


def signedup(request):
    return render(request, 'signedup.html')


