#!/usr/bin/env python3
import os
import time
import socket
import time
from datetime import datetime
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

'''
Vdd = 3.3 V
Resistor = 4.7k (Liga Vdd com entrada de dados)
Entrada de dados = GPIO PIN 4
'''

# Carregar modulos do SO
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

# Iformacoes do host
dir_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostname()

# Configuracoes dos diretorios W1
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


# Credenciais do Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dir_path, 'secret_key.json'), scope)
client = gspread.authorize(creds)
# Abre uma o documeto (spreadsheet)
spreadsheet = client.open(hostname)
# Abre a planilha (worksheet)
worksheet = spreadsheet.worksheet('temperatura-cpu')

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	return(res.replace('temp=', '').replace("'C\n", ''))


while (True):
	temperatura = float(getCPUtemperature())

	# data : hora, temperatura
	row = [datetime.now().strftime('%d/%m/%Y %H:%M:%-S'), temperatura]

	try :
		worksheet.append_row(row)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados para a nuvem')

	try:
		with open(os.path.join(dir_path, 'log-temperatura.csv'), 'a') as f:
			w = csv.writer(f)
			w.writerow(row)
	except Exception as e:
		print(e)
		print('Erro ao salvar dado em log-temperatura.csv')

	time.sleep(10)


# Loop principal
while True:
	for folder in device_folders:
		if folder[0:2] != '28':
			#print(folder)
			continue
		print(read_temp(folder))
		time.sleep(1)
