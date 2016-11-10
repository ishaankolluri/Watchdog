import json
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from ..models import Position, Instrument
from .. import views


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
        with self.assertRaises(TypeError) as context:
            self.client.get(reverse('simulator:profile'))
        self.assertIn(
            "\'AnonymousUser\' object is not iterable",
            context.exception.message)

    def test_login_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        # If this works, we can check the context of the view.
        response = self.client.get(reverse('simulator:login'))
        self.assertIn("loginForm", response.content)

    def test_signup_view(self):
        response = self.client.get(reverse('simulator:signup'))
        self.assertIn("Sign Up", response.content)

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

    def test_home_view(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        response = self.client.get(reverse('simulator:home'))
        self.assertIn("Stock Market Company Lookup", response.content)

    def test_getstockdata_views(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "PIH"
        })
        request.user = self.user
        response = views.getstockdata_views(request)
        # Test the non-UI view has returned a valid response.
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content)[0]
        # Test that the JSON returned has a trade price.
        self.assertIn("LastTradePrice", json_response)

    def test_market_execution(self):
        # Note that market_execution is dependent on getting stock data.
        self.client.login(username="ishaankolluri", password="watchdog")
        request = self.factory.get(reverse('simulator:getstockdata_views'), {
            "query": "PIH"
        })
        request.user = self.user
        response = views.getstockdata_views(request)
        self.assertEqual(response.status_code, 200)
        # The view controller should be tracking the right instrument.
        current_quantity = Position.objects.get(
            user=self.user,
            symbol="PIH",
        ).quantity_purchased
        self.assertEqual("PIH", views.CURRENT_STOCK_MODAL["StockSymbol"])
        request = self.factory.post(reverse('simulator:market_execution'), {
            "quantity": "5",
            "market": "buy",
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
        # The URL should have redirected (302) to the home URL successfully.
        self.assertEqual(response.status_code, 302)

        # Perform the same operation test for a market sell.
        request = self.factory.post(reverse('simulator:market_execution'), {
            "quantity": "5",
            "market": "sell",
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

    def test_leaderboard(self):
        self.client.login(username="ishaankolluri", password="watchdog")
        user_two = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="test",
        )
        user_two.save()
        Position.objects.create(
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
