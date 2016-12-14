'''
This is the cron task that needs to be scheduled
'''
from django_cron import CronJobBase, Schedule
import datetime
from models import *
from googlefinance import getQuotes

class MyCronJob(CronJobBase):
	print("Cronjob scheduled..................OK")
	RUN_EVERY_MINS = 0
	schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
	code = 'simulator.my_cron_job' # a unique code
	def do(self):
		ins_set = Instrument.objects.all()
		for ins in ins_set:
			updated_price = getQuotes([ins.symbol, 'NASDAQ'])[0]["LastTradePrice"]
			ins.update_price(updated_price)
		
		