from __future__ import unicode_literals

from decimal import Decimal 
from django.db import models
from django.contrib.auth.models import User


class Instrument(models.Model):
    symbol = models.CharField(max_length=10)
    current_price = models.DecimalField(decimal_places=3, max_digits=10)
    last_time_updated = models.DateTimeField()

    # TODO: Needs to be an atomic transaction.
    def update_price(self, retrieved_price):
        self.current_price = Decimal(retrieved_price)
        self.save()

    def __str__(self):
        return "Symbol: {} | Current Price: {}".format(
            self.symbol,
            self.current_price,
        )


class Position(models.Model):
    user = models.ForeignKey(User, related_name="user")
    instrument = models.ForeignKey(
        Instrument, on_delete=models.CASCADE, related_name="instrument")
    symbol = models.CharField(max_length=10)
    quantity_purchased = models.PositiveIntegerField()
    price_purchased = models.DecimalField(decimal_places=3, max_digits=10)
    date_purchased = models.DateTimeField()

    # TODO: Needs to be an atomic transaction.
    def market_buy(self, quantity):
        self.quantity_purchased += Decimal(quantity)
        self.save()
        return True

    def market_sell(self, quantity):
        if Decimal(quantity) > self.quantity_purchased:
            return False
        else:
            self.quantity_purchased -= Decimal(quantity)
            self.save()
            return True

    @property
    def net_profit(self):
        return self.quantity_purchased * (
            self.instrument.current_price - self.price_purchased)

    def __str__(self):
        return ("Symbol: {} | User: {} | Quantity: {}"
                " | Price Purchased: {} | Current Price: {}".
                format(self.symbol, self.user, self.quantity_purchased,
                       self.price_purchased, self.instrument.current_price, )
                )
