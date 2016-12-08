import json
import os
import glob
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from ..models import Position, Instrument
from .. import views
from ..forms import *


class UITests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ishaankolluri",
            email="isk2108@columbia.edu",
            password="watchdog",
        )
        self.user.save()
        self.instrument = Instrument.objects.create(
            symbol="PIH",
            current_price=Decimal(50.00),
            last_time_updated=datetime.now(),
        )
        self.instrument.save()
        self.position = Position.objects.create(
            user=self.user,
            instrument=self.instrument,
            symbol="PIH",
            price_purchased=Decimal(45.00),
            quantity_purchased=2,
            date_purchased=datetime.now(),
        )
        self.client = Client()
        self.factory = RequestFactory()

    def test_secure_page(self):
        # Test that the user cannot access restricted pages without logging in.
        response = self.client.get(reverse('simulator:profile'))
        self.assertIn("loginForm", response.content)
        # Now log in the user - this should return a valid response.
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.get(reverse('simulator:profile'))
        # Our username should be displayed on all restricted views.
        self.assertIn("ishaankolluri", response.content)
        print("Secure Page view.............................OK")

    def test_home_not_auth(self):
        response = self.client.get(reverse('simulator:home'))
        self.assertEqual(response.status_code, 403)

    def test_market_not_auth(self):
        response = self.client.get(reverse('simulator:market_execution'))
        self.assertEqual(response.status_code, 403)

    def test_market_not_get_request(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.post(reverse('simulator:market_execution'))
        self.assertEqual(response.status_code, 400)

    def test_login_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        # If this works, we can check the context of the view.
        response = self.client.get(reverse('simulator:login'))
        self.assertIn("loginForm", response.content)
        print("Login view.............................OK")

    def test_logout_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.get(reverse('simulator:logout'))
        self.assertEqual(response.status_code, 302)

    def test_legal_logged_in_view(self):
        data = {
            "username": "ishaankolluri",
            "email": "ishaankolluri@gmail.com",
            "password": "watchdog",
        }
        response = self.client.post(reverse('simulator:loggedin'), data)
        self.assertEqual(response.status_code, 302)

    def test_illegal_logged_in_view(self):
        data = {
            "username": "fake",
            "email": "nonexistent@gmail.com",
            "password": "watchCAT",
        }
        response = self.client.post(reverse('simulator:loggedin'), data)
        self.assertIn(response.content, "Login")

    def test_signup_view(self):
        response = self.client.get(reverse('simulator:signup'))
        self.assertIn("Sign Up", response.content)
        print("Signup view.............................OK")

    def test_confirm_signup_view(self):
        data = {
            "username": "user",
            "first_name": "user",
            "email": "user@gmail.com",
            "password": "user",
        }
        response = self.client.post(reverse('simulator:signup'), data)
        self.assertEqual(response.status_code, 302)

    def test_profile_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.get(reverse('simulator:profile'))
        # Tests the portfolio contains all user positions created.
        self.assertIn('PIH', response.content)
        i = Instrument.objects.create(
            symbol="MSFT",
            current_price=Decimal(50.00),
            last_time_updated=datetime.now(),
        )
        i.save()
        p = Position.objects.create(
            user=self.user,
            instrument=i,
            symbol="MSFT",
            price_purchased=Decimal(55.00),
            quantity_purchased=2,
            date_purchased=datetime.now(),
        )
        p.save()
        # Test the profile contains new positions created in the DB.
        response = self.client.get(reverse('simulator:profile'))
        self.assertIn("MSFT", response.content)
        # Test the profile reflects changes to existing positions.
        p.quantity_purchased = 5
        p.save()
        response = self.client.get(reverse('simulator:profile'))
        # MSFT is the only stock that should have a quantity of 5.
        self.assertIn("<td>5</td>", response.content)
        print("Profile view.............................OK")

    def test_home_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.get(reverse('simulator:home'))
        self.assertIn("Stock Market Company Lookup", response.content)
        print("Home view.............................OK")

    def test_getstockdata_views(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "PIH"
        })
        request.user = self.user
        response = views.getstockdata_views(request)
        # Test if the graph was created for the stock
        timestamp = str(json.loads(response.content)[0]['LookupTimestamp'])
        if(os.path.exists("simulator/static/stock-graph" + timestamp + ".png")):
            print("Stock Graph created.........................OK")
        else:
            raise Exception("Stock Graph not created")
        #Now delete the graph. Test for deletion implemented towards the end
        request_delete = ""
        views.delete_image(request_delete)
        # Test the non-UI view has returned a valid response.
        self.assertEqual(response.status_code, 200)
        
        json_response = json.loads(response.content)[0]
        # Test that the JSON returned has a trade price.
        self.assertIn("LastTradePrice", json_response)
        print("GetStockData view.............................OK")

    def test_leaderboard(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        user_two = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="test",
        )
        user_two.save()
        pos_two = Position.objects.create(
            user=user_two,
            instrument=self.instrument,
            symbol="PIH",
            price_purchased=Decimal(50.00),
            quantity_purchased=2,
            date_purchased=datetime.now(),
        )
        request = self.factory.get(reverse('simulator:leaderboard'))
        request.user = self.user
        response = views.leaderboard(request)
        # Not that self.user is first and user_two should be second.
        # The whitespace is for syntactic sugar.
        self.assertIn(
            "<td>1</td>\n                    "
            "<td>ishaankolluri</td>\n", response.content)
        self.assertIn(
            "<td>2</td>\n                    "
            "<td>test_user</td>\n", response.content)
        print("Leaderboard view.............................OK")


    def test_delete_image(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request_create = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "PIH"
        })
        request_create.user = self.user
        views.getstockdata_views(request_create)
        request_delete = ""
        response = views.delete_image(request_delete)
        if not glob.glob("simulator/static/stock-graph*"):
            print "Stock Graph deleted............................OK"
        else:
            raise Exception("Stock Graph not deleted")
        print("Delete Graph view.............................OK")


class MarketExecutionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="ishaankolluri",
            email="isk2108@columbia.edu",
            password="watchdog",
        )
        self.user.save()
        self.instrument = Instrument.objects.create(
            symbol="PIH",
            current_price=Decimal(50.00),
            last_time_updated=datetime.now(),
        )
        self.instrument.save()
        self.position = Position.objects.create(
            user=self.user,
            instrument=self.instrument,
            symbol="PIH",
            price_purchased=Decimal(45.00),
            quantity_purchased=2,
            date_purchased=datetime.now(),
        )
        self.client = Client()
        self.factory = RequestFactory()

    def test_market_execution_old_buy(self):
        # Note that market_execution is dependent on getting stock data.
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "PIH"
        })
        request.user = self.user
        response = views.getstockdata_views(request)
        # Delete stock graph
        request_delete = ""
        views.delete_image(request_delete)
        self.assertEqual(response.status_code, 200)
        # The view controller should be tracking the right instrument.
        current_quantity = Position.objects.get(
            user=self.user,
            symbol="PIH",
        ).quantity_purchased
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "PIH",
            "price": "59.02",
            "quantity": "5",
            "execution": "buy",

        })
        request.user = self.user
        # Adjust unit testing for Django message bug.
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        response = views.market_execution(request)
        executed_buy_quantity = Position.objects.get(
            user=self.user,
            symbol="PIH",
        ).quantity_purchased
        # The market should have successfully made a buy.
        self.assertEqual(current_quantity + 5, executed_buy_quantity)
        self.assertEqual(response.status_code, 200)
        print("MarketExecution OldBuy view...................OK")
    
    def test_market_execution_new_buy(self):    
        self.client.login(username="ishaankolluri", password="watchdog")
        # Perform a market buy on a brand new stock - MSFT.
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "MSFT"
        })
        request.user = self.user
        views.getstockdata_views(request)
        request_delete = ""
        views.delete_image(request_delete)
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "MSFT",
            "price": "59.02",
            "quantity": "5",
            "execution": "buy",
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        views.market_execution(request)
        new_ins = Instrument.objects.get(symbol="MSFT")
        self.assertIsNotNone(new_ins)
        new_pos = Position.objects.get(instrument=new_ins)
        self.assertIsNotNone(new_pos)
        print("MarketExecution NewBuy view................OK")

    def market_execution_owned_sell(self):    
        self.client.login(username="ishaankolluri", password="watchdog")
        # Perform the same operation test for a market sell.
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "PIH",
            "price": "59.02",
            "quantity": "5",
            "execution": "sell",
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        current_quantity = Position.objects.get(
            user=self.user,
            symbol="PIH",
        ).quantity_purchased
        response = views.market_execution(request)
        executed_sell_quantity = Position.objects.get(
            user=self.user,
            symbol="PIH",
        ).quantity_purchased
        self.assertEqual(current_quantity - 5, executed_sell_quantity)
        self.assertEqual(response.status_code, 302)
        print("MarketExecution OwnedSell view.............................OK")

    def market_execution_NOT_owned_sell(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        # Attempt and fail a market sell on a stock you don't own.
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "AVHI"
        })
        request.user = self.user
        views.getstockdata_views(request)
        request_delete = ""
        views.delete_image(request_delete)
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "AVHI",
            "price": "59.02",
            "quantity": "5",
            "execution": "sell",
        })
        request.user = self.user
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        views.market_execution(request)
        new_ins = Instrument.objects.get(symbol="AVHI")
        self.assertIsNotNone(new_ins)
        new_pos_list = Position.objects.filter(
            instrument=new_ins, user=self.user)
        self.assertEquals(new_pos_list.count(), 0)
        print("MarketExecution NotOwnedSell view.............................OK")

    def test_initial_buy_500(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "AVHI"
        })
        request.user = self.user
        views.getstockdata_views(request)
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "AVHI",
            "price": "59.02",
            "quantity": "501",
            "execution": "buy",
        })
        request.user = self.user
        response = views.market_execution(request)
        self.assertIn(json.loads(response.content)["message"],
                      "Please buy less than 500 stocks at a time.")

    def test_illegal_sell(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "AVHI"
        })
        request.user = self.user
        views.getstockdata_views(request)
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "AVHI",
            "price": "59.02",
            "quantity": "501",
            "execution": "sell",
        })
        request.user = self.user
        response = views.market_execution(request)
        self.assertIn(json.loads(response.content)["message"],
                      "You cannot sell a stock you do not own.")

    def test_full_position_sell(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "AVHI"
        })
        request.user = self.user
        views.getstockdata_views(request)
        request = self.factory.get(reverse('simulator:market_execution'), {
            "symbol": "PIH",
            "price": "45.00",
            "quantity": "2",
            "execution": "sell",
        })
        self.assertEqual(2, Position.objects.get(
            user=self.user, symbol="PIH").quantity_purchased)
        request.user = self.user
        response = views.market_execution(request)
        self.assertIn(json.loads(response.content)["message"],
                      "You have placed a market sell.")
        pos_list = Position.objects.filter(user=self.user, symbol="PIH")
        self.assertEqual(pos_list.count(), 0)
