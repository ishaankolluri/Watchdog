import json
from googlefinance import getQuotes

from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET

from simulator.forms import UserForm, LoginForm
from simulator.models import Instrument, Position
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login, logout


def is_authenticate(request):
    return request.user.is_authenticated


def home(request):
    if is_authenticate(request):
        # print(request.user)
        return render(request, 'home.html')
    else:
        return HttpResponseRedirect(reverse('simulator:login'))


def getstockdata_views(request):
    query_str = str(request.GET['query'])
    print(query_str)
    p = json.dumps(getQuotes(query_str))    
    print(p)
    return HttpResponse(p, content_type="application/json")


def loggedin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect("/")
        else:
            return HttpResponseRedirect(reverse('simulator:login'))
    # return HttpResponseRedirect(reverse('simulator:home'))


def market_execution(request):
    if request.POST:
        print ("Success")
    # return HttpResponseRedirect(reverse('simulator:home'))
    return render(request, 'home.html')


def login_req(request):
    return render(request, 'login.html')

def logout_req(request):
    logout(request)
    return HttpResponseRedirect("/login")


def signup(request):
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(**form.cleaned_data)
            user.save()
            login(request, user)
            return HttpResponseRedirect("/")
    else:
        form = UserForm()
    return render(request, 'signup.html', {'form':form})


def signedup(request):
    return render(request, 'signedup.html')


def profile(request):
    # Assuming that this view has access to the user.
    # print(request.user.username)
    # print(request.user.password)
    user = request.user
    context = {}
    context["user"] = user;
    print(user.password)
    positions = Position.objects.filter(user=request.user)
    # position = Position.objects.get(user=request.user)
    portfolio_value = 0
    for position in positions:
        i = Instrument.objects.get(symbol=position.symbol)
        # TODO: Get updated price for every instrument the user has a position in.
        # TODO: Use Google Finance?
        portfolio_value = (portfolio_value + position.price_purchased - i.current_price)
        print(position.net_profit)
    print(positions)
    context["portfolio_value"] = portfolio_value
    context["positions"] = positions

    return render(request, 'profile.html', context=context)
    # return render(request, 'profile.html')

