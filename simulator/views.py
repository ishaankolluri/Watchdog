import ast, datetime, json
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


CURRENT_STOCK_MODAL = ""


def is_authenticate(request):
    return request.user.is_authenticated


def home(request):
    if is_authenticate(request):
        return render(request, 'home.html')
    else:
        return HttpResponseRedirect(reverse('simulator:login'))


def getstockdata_views(request):
    query_str = str(request.GET['query'])
    p = json.dumps(getQuotes(query_str))
    global CURRENT_STOCK_MODAL
    CURRENT_STOCK_MODAL = json.loads(p)[0]
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
    user = request.user
    symbol = CURRENT_STOCK_MODAL["StockSymbol"]
    quantity = request.POST["quantity"]
    execution = request.POST["market"]
    last_trade_price = CURRENT_STOCK_MODAL["LastTradePrice"]

    ins_set = Instrument.objects.filter(symbol=symbol)
    if ins_set.count() == 0:
        # Add local instruments to DB on an as-needed basis.
        ins = Instrument.objects.create(
            symbol=symbol,
            current_price=last_trade_price,
            last_time_updated=datetime.datetime.now(),
        )
    else:
        ins = Instrument.objects.get(symbol=symbol)
    # Check if user has a position.
    pos_list = Position.objects.filter(user=user, instrument=ins)
    if pos_list.count() == 0:
        if execution == "buy":
            Position.objects.create(
                user=user,
                instrument=ins,
                symbol=symbol,
                price_purchased=last_trade_price,
                quantity_purchased=quantity,
                date_purchased=datetime.datetime.now(),
            )
    else:
        pos = Position.objects.get(user=user, instrument=ins)
        if execution == "buy":
            pos.quantity_purchased += quantity
            pos.save()
        if execution == "sell":
            if quantity > pos.quantity_purchased:
                # Raise some error.
                print "no"
            else:
                pos.quantity_purchased -= quantity
                pos.save()

    return HttpResponseRedirect(reverse("simulator:home"))


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
    # How do I access the user data in the request?
    print request.POST
    return render(request, 'profile.html')
