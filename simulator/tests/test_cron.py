from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from ..cron import MyCronJob
from ..models import Position, Instrument

class CronTests(TestCase):

    def setUp(self):
        self.ins = Instrument.objects.create(
            symbol="PIH",
            current_price=Decimal(1.00),
            last_time_updated=datetime.now(),
        )

    def test_cron(self):
        MyCronJob().do()
        self.assertNotEqual(self.ins.current_price, Decimal('1.00'))
