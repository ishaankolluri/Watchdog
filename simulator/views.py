import datetime
import os
import glob
from decimal import Decimal
import json
from googlefinance import getQuotes
import pandas as pd
from pandas_datareader import data as web
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from simulator.forms import UserForm
from simulator.models import Instrument, Position
import time


def is_authenticate(request):
    return request.user.is_authenticated


def home(request):
    if is_authenticate(request):
        return render(request, 'home.html')
    else:
        return HttpResponseRedirect(reverse('simulator:login'))


def getstockdata_views(request):
    query_str = str(request.GET['query'])
    mydict = []
    mydict.append(getQuotes(query_str)[0])
    lookuptimestamp = time.time()
    mydict[0]['LookupTimestamp'] = str(lookuptimestamp)
    p = json.dumps(mydict)
    plt.rcParams['axes.facecolor'] = '#33cc33'
    end = datetime.datetime.now()
    start = datetime.datetime(end.year-1,end.month,end.day)
    df = web.DataReader(query_str, "yahoo", start, end)
    plots = df[['Close']].plot(subplots=True, figsize=(10, 10), color='#3333ff', linewidth = 1.5)
    plt.grid()
    plt.title(query_str)
    filename = "simulator/static/" + "stock-graph" + str(lookuptimestamp) + ".jpg"
    plt.savefig(filename)
    return HttpResponse(p, content_type="application/json")


def delete_image(request):
    print "************************************In delete image*****************************************"
    for f in glob.glob("simulator/static/stock-graph*"):
        os.remove(f)
    p=[1,2,3] # just passing random values to check reception
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

def market_execution(request):
    user = request.user
    symbol = request.GET.get('symbol')
    quantity = request.GET.get('quantity')
    execution = request.GET.get('execution')
    last_trade_price = request.GET.get('price')
    ins_set = Instrument.objects.filter(symbol=symbol)
    if ins_set.count() == 0:
        ins = Instrument.objects.create(
            symbol=symbol,
            current_price=last_trade_price,
            last_time_updated=datetime.datetime.now(),
        )
    else:
        ins = Instrument.objects.get(symbol=symbol)
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
            # Selling a stock you don't own.
            messages.success(
                request, "You cannot sell a stock you do not own.")
    else:
        pos = Position.objects.get(user=user, instrument=ins)
        if execution == "buy":
            if pos.market_buy(quantity):
                messages.success(
                    request, "You have placed a market buy.")
            else:
                messages.success(
                    request,
                    "Your market buy wasn't processed. "
                    "Please buy less than 500 stocks at a time.")
        if execution == "sell":
            if pos.market_sell(quantity):
                if pos.quantity_purchased == 0:
                    pos.delete()
                messages.success(request, "You have placed a market sell.")
            else:
                messages.success(
                    request,
                    'Please do not attempt to sell more '
                    'than you currently own of this stock.')
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
    return render(request, 'signup.html', {'form': form})


def signedup(request):
    return render(request, 'signedup.html')


def profile(request):
    user = request.user
    context = {"user": user}
    positions = Position.objects.filter(user=request.user)
    portfolio_value = 0
    for position in positions:
        i = Instrument.objects.get(symbol=position.symbol)
        updated_price = getQuotes([position.symbol, 'NASDAQ'])[0]["LastTradePrice"]
        i.update_price(updated_price)
        portfolio_value = portfolio_value + (position.instrument.current_price * position.quantity_purchased)
    context["portfolio_value"] = portfolio_value
    context["positions"] = positions
    return render(request, 'profile.html', context=context)


def leaderboard(request):
    users = User.objects.all()
    user_list = []
    context = {}
    for user in users:
        portfolio_value, net_plus_minus = _update_and_return_user_portfolio_value(user)
        user_struct = {
            "user": user,
            "portfolio_value": portfolio_value,
            "net_plus_minus": net_plus_minus,
        }
        user_list.append(user_struct)
    user_list = sorted(user_list, key=lambda k: k['portfolio_value'], reverse=True)
    context["users"] = user_list
    return render(request, 'leaderboard.html', context=context)


def _update_and_return_user_portfolio_value(user):
    positions = Position.objects.filter(user=user)
    portfolio_value = 0
    net_plus_minus = 0
    for position in positions:
        i = position.instrument
        updated_price = getQuotes(
            [position.symbol, 'NASDAQ'])[0]["LastTradePrice"]
        i.update_price(updated_price)
        portfolio_value = portfolio_value + (i.current_price * position.quantity_purchased)
        net_plus_minus = net_plus_minus + (i.current_price - position.price_purchased) * position.quantity_purchased
    return portfolio_value, net_plus_minus
