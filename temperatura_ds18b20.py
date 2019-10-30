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
	Entrada de dados = GPIO4
'''

# Carregar modulos do SO
#os.system('modprobe w1-gpio')
#os.system('modprobe w1-therm')

# Informacoes do host
dir_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostname()
# Configuracoes dos diretorios W1
base_dir = '/sys/bus/w1/devices/'
device_folders = os.listdir(base_dir)

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

def log_local(device, data):
	try:
		with open(os.path.join(dir_path, 'logs-temperatura', device + '.csv'), 'a') as f:
			w = csv.writer(f)
			w.writerow(data)
	except Exception as e:
		print(e)
		print('Erro ao salvar dado em arquivo .csv')

def log_nuvem(device, data):
	# Credenciais do Google Drive API
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dir_path, 'secret_key.json'), scope)
	client = gspread.authorize(creds)
	# Abre uma o documeto (spreadsheet)
	spreadsheet = client.open(hostname)
	# Todas as worksheets
	ws_list = spreadsheet.worksheets()
	worksheet = None

	# Abre a planilha (worksheet)
	for ws in ws_list:
		if ws.title == device:
			worksheet = spreadsheet.worksheet(device)
			break
	# Se nao existe, cria
	if worksheet == None:
		worksheet = spreadsheet.add_worksheet(title=device, rows='100', cols='2')
		worksheet.append_row(['Data Hora', 'Temperatura'])
	# Escreve
	try:
		worksheet.append_row(data)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados para a nuvem')

# Bloco principal
def main():
	devices = dict()
	for folder in device_folders:
		if folder[0:2] != '28':
			continue

		# data e hora, temperatura
		data = [datetime.now().strftime('%d/%m/%Y %H:%M:%-S'), read_temp(folder)]
		devices[folder] = data

	# Registra o log separadamente (local primeiro)
	for device, data in devices.items():
		log_local(device, data)
	# TODO: descomentar
	for device, data in devices.items():
		log_nuvem(device, data)
		time.sleep(7)


if __name__ == '__main__':
	main()
