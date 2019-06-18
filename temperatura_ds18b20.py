#!/usr/bin/env python3
import os
import time
import socket
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

# Informacoes do host
dir_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostname()

# Credenciais do Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dir_path, 'secret_key.json'), scope)
client = gspread.authorize(creds)
# Abre uma o documeto (spreadsheet)
spreadsheet = client.open(hostname)


# Configuracoes dos diretorios W1
base_dir = '/sys/bus/w1/devices/'

def read_temp_raw(device_file):
	try:
		f = open(os.path.join(base_dir, device_file), 'r')
		lines = f.readlines()[-1] # ultima linha somente
		f.close()
	except FileNotFoundError as fnf:
		print(fnf)
		print('Sensor removido =/')
	return lines

def read_temp(folder):
	line = read_temp_raw(os.path.join(folder, 'w1_slave'))
	equals_pos = line.find('t=')
	if equals_pos != -1:
		temp_string = line[equals_pos + 2:]
		temp_c = float(temp_string) / 1000
		return temp_c

def getCPUtemperature():
	res = os.popen('vcgencmd measure_temp').readline()
	return(res.replace('temp=', '').replace("'C\n", ''))


# Bloco principal
#### TODO: criar uma lista com os dispositivos e chamar o log local para todos e depois o log em nuvem
device_folders = os.listdir(base_dir)
for folder in device_folders:
	if folder[0:2] != '28':
		continue

	# Todas as worksheets
	ws_list = spreadsheet.worksheets()
	worksheet = None

	# Abre a planilha (worksheet)
	for ws in ws_list:
		if ws.title == folder:
			worksheet = spreadsheet.worksheet(folder)
			break
	# Se nao existe, cria
	if worksheet == None:
		worksheet = spreadsheet.add_worksheet(title=folder, rows='100', cols='2')
		worksheet.append_row(['Data Hora', 'Temperatura'])

	# data e hora, temperatura
	row = [datetime.now().strftime('%d/%m/%Y %H:%M:%-S'), read_temp(folder)]

	try:
		worksheet.append_row(row)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados para a nuvem')

	try:
		with open(os.path.join(dir_path, 'logs-temperatura' ,folder + '.csv'), 'a') as f:
			w = csv.writer(f)
			w.writerow(row)
	except Exception as e:
		print(e)
		print('Erro ao salvar dado em arquivo .csv')
