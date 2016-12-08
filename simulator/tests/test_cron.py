from datetime import datetime

from django.test import TestCase

from .. import cron
from ..models import *


class CronTests(TestCase):

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

    def test_cron_update_instruments(self):
        cron.update_instruments()
        self.assertNotEqual(self.instrument.current_price, Decimal(50.00))
