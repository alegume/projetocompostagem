#!/usr/bin/env python3
import os
import time
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folders = os.listdir(base_dir)
device_folders.remove('w1_bus_master1')
 
def read_temp_raw(device_file):
	f = open(os.path.join(base_dir, device_file), 'r')
	lines = f.readlines()[-1] # ultima linha somente
	f.close()
	return lines
 
def read_temp(folder):
	line = read_temp_raw(os.path.join(folder, 'w1_slave'))
	equals_pos = line.find('t=')
	if equals_pos != -1:
		temp_string = line[equals_pos + 2:]
		temp_c = float(temp_string) / 1000
		return (folder, temp_c)
	
while True:
	for folder in device_folders:
		print(read_temp(folder))
		time.sleep(1)
