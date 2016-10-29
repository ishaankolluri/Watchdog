import json
from googlefinance import getQuotes

from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_GET

from simulator.forms import UserForm
from simulator.models import Instrument, Position
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string


def home(request):
    return render(request, 'home.html')


def getstockdata_views(request):
    query_str = str(request.GET['query'])
    print(query_str)
    p = json.dumps(getQuotes(query_str))    
    print(p)
    return HttpResponse(p, content_type="application/json")


def market_execution(request):
    if request.POST:
        print "Success"
    # return HttpResponseRedirect(reverse('simulator:home'))
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
    # Assuming that this view has access to the user.
    # context = {}
    # context["user"] = user

    # positions = Position.objects.get(user=user)
    # portfolio_value = 0
    # instruments = []
    # for position in positions:
    #     i = Instrument.objects.get(symbol=position.symbol)
        # TODO: Get updated price for every instrument the user has a position in.
        # TODO: Use Google Finance?
    #     portfolio_value = (portfolio_value + position.price_purchased - i.current_value)
    #     instruments.append(i)
    # context["portfolio_value"] = portfolio_value
    # context["positions"] = positions
    # context["instruments"] = instruments
    # return render(request, 'profile.html', context=context)
    return render(request, 'profile.html')
