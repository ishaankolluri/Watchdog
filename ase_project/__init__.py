'''
init.py is called every time the application starts or when 
the cron job executes. We just want to start the cron 
script once for which we have implemented a not-so-clean method
'''

from pathlib import Path
one_time_file = Path('one_time_file')
if not one_time_file.is_file():
	from subprocess import Popen
	p = Popen(['./ase_project/cronjob.sh'])
	print "Cronjob started...........OK"
	f = open('one_time_file','w')
	f.close()
	print "one_time_file created"
