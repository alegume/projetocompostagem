#!/usr/bin/env python3
import os
import time
import csv

# Return CPU temperature as a character string
def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	return(res.replace('temp=', '').replace("'C\n", ''))

while (True):
	temperatura = float(getCPUtemperature())

	# data : hora, temperatura
	row = [time.ctime(), temperatura] 

	with open('log-temperatura.csv', 'a') as f:
		w = csv.writer(f)
		w.writerow(row)
	
	time.sleep(5)
