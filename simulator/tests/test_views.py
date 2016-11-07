from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.test.client import RequestFactory
from django.core.urlresolvers import reverse

from ..models import Position, Instrument
from . import views

class UITests(TestCase):
    def setUp(self):
        print "Starting tests"


class MarketTests(TestCase):
    def setUp(self):
        print "Starting tests"

