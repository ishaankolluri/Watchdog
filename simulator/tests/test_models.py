from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from ..models import Position, Instrument


class InstrumentTests(TestCase):
    def setUp(self):
        self.ins = Instrument.objects.create(
            symbol="PIH",
            current_price=Decimal(50.00),
            last_time_updated=datetime.now(),
        )

    def test_update_price(self):
        updated_price = "60.00"
        self.ins.update_price(updated_price)
        self.assertEqual(Decimal(60.00), self.ins.current_price)
        # Test with number rather than string.
        updated_price = 70.00
        self.ins.update_price(updated_price)
        self.assertEqual(Decimal(70.00), self.ins.current_price)

    def test_str(self):
        serial_str = "Symbol: PIH | Current Price: 50"
        self.assertEqual(serial_str, self.ins.__str__())


class PositionTests(TestCase):
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
        self.position.save()

    def test_market_buy(self):
        buy_quantity = "5"
        pre_buy_quantity = self.position.quantity_purchased
        success = self.position.market_buy(buy_quantity)
        self.assertTrue(success)
        self.assertEqual(
            pre_buy_quantity + 5, self.position.quantity_purchased)

    def test_market_sell(self):
        self.position.quantity_purchased = 9
        self.position.save()
        sell_quantity = "7"
        pre_sell_quantity = self.position.quantity_purchased
        success = self.position.market_sell(sell_quantity)
        self.assertTrue(success)
        self.assertEqual(
            pre_sell_quantity - 7, self.position.quantity_purchased)
        # Attempt to fail the market sell by selling more than what is owned.
        self.position.quantity_purchased = 5
        self.position.save()
        pre_sell_quantity = self.position.quantity_purchased
        sell_quantity = "7"
        failure = self.position.market_sell(sell_quantity)
        self.assertFalse(failure)
        self.assertEqual(
            pre_sell_quantity, self.position.quantity_purchased)

    def test_net_profit(self):
        known_profit = self.position.quantity_purchased * (
            self.instrument.current_price - self.position.price_purchased)
        self.assertEqual(known_profit, self.position.net_profit)

    def test_str(self):
        self.position.quantity_purchased = 2
        self.position.price_purchased = Decimal(45.00)
        self.position.instrument.current_price = Decimal(50.00)
        serial_str = "Symbol: PIH | User: ishaankolluri | Quantity: 2 |" \
                     " Price Purchased: 45 | Current Price: 50"
        self.assertEqual(serial_str, self.position.__str__())
