from datetime import datetime
from models import *
from googlefinance import getQuotes


def update_instruments():
    print "Executing update instruments cron at " + str(datetime.now())
    ins_set = Instrument.objects.all()
    for ins in ins_set:
        updated_price = getQuotes(
            [ins.symbol, 'NASDAQ'])[0]["LastTradePrice"]
        print updated_price
        ins.update_price(updated_price)
    print "Completed update instruments cron at " + str(datetime.now())



