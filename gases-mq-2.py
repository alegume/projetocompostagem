#!/usr/bin/python3

from GasDetection.gas_detection import GasDetection
import os
import time
import socket
from datetime import datetime
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Informacoes do host
dir_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostname()

# Credenciais do Google Drive API
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dir_path, 'secret_key.json'), scope)
client = gspread.authorize(creds)
# Abre uma o documeto (spreadsheet)
spreadsheet = client.open(hostname)

def salvar_local(gases, hora):
	for gas, valor in gases.items():
		## TODO: REMOVER
		print('{}: {} ppm'.format(gas, valor))
		# data e hora, valor
		row = [hora, float(valor)]
		try:
			with open(os.path.join(dir_path, 'logs-gas-' , gas + '.csv'), 'a') as f:
				w = csv.writer(f)
				w.writerow(row)
		except Exception as e:
			print(e)
			print('Erro ao salvar dado em arquivo .csv')

def salvar_nuvem(gases, hora):
	for gas, valor in gases.items():
		# Todas as worksheets
		ws_list = spreadsheet.worksheets()
		worksheet = None

		# Abre a planilha (worksheet)
		for ws in ws_list:
			if ws.title == gas:
				worksheet = spreadsheet.worksheet(gas)
				break
		# Se nao existe, cria
		if worksheet == None:
			worksheet = spreadsheet.add_worksheet(title=gas, rows='100', cols='2')
			worksheet.append_row(['Data', 'Valor (PPM)'])

		# data e hora, valor
		row = [hora, float(valor)]
		try:
			worksheet.append_row(row)
		except Exception as e:
			print(e)
			print('Erro ao enviar dados para a nuvem')

		time.sleep(7)

def main():
	print('Calibrando ...')
	#### TODO: colocar o fator como constante
	#### TODO: refazer esquema da temperatura
	detection = GasDetection(pin=0)

	ppm = detection.percentage()
	hora = datetime.now().strftime('%d/%m/%Y %H:%M:%-S')

	# Nao é possível criar worksheet com numeros
	gases = {'CO': ppm[detection.CO_GAS],
		'H-dois': ppm[detection.H2_GAS],
		'CH-quatro': ppm[detection.CH4_GAS],
		'LPG': ppm[detection.LPG_GAS],
		'PROPANO': ppm[detection.PROPANE_GAS],
		'ALCOOL': ppm[detection.ALCOHOL_GAS],
		'FUMACA': ppm[detection.SMOKE_GAS]
	}

	# Registra o log separadamente (local primeiro)
	salvar_local(gases, hora)
	salvar_nuvem(gases, hora)


if __name__ == '__main__':
	main()