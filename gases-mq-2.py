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



def main():
	print('Calibrando ...')
	detection = GasDetection(pin=0)

	try:
		while True:
			ppm = detection.percentage()

			gases = {'CO': ppm[detection.CO_GAS],
				'H2': ppm[detection.H2_GAS],
				'CH4': ppm[detection.CH4_GAS],
				'LP4': ppm[detection.LPG_GAS],
				'PROPANO': ppm[detection.PROPANE_GAS],
				'ALCOOL': ppm[detection.ALCOHOL_GAS],
				'FUMACA': ppm[detection.SMOKE_GAS]
			}

			print('CO: {} ppm'.format(ppm[detection.CO_GAS]))
			print('H2: {} ppm'.format(ppm[detection.H2_GAS]))
			print('CH4: {} ppm'.format(ppm[detection.CH4_GAS]))
			print('LPG: {} ppm'.format(ppm[detection.LPG_GAS]))
			print('PROPANO: {} ppm'.format(ppm[detection.PROPANE_GAS]))
			print('ÁLCOOL: {} ppm'.format(ppm[detection.ALCOHOL_GAS]))
			print('FUMAÇA: {} ppm\n'.format(ppm[detection.SMOKE_GAS]))

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

				# data e hora, temperatura
				row = [datetime.now().strftime('%d/%m/%Y %H:%M:%-S'), read_temp(folder)]

				try :
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

			time.sleep(3)

	except KeyboardInterrupt:
		print('\nUsuário abortou o processo =/')

if __name__ == '__main__':
	main()
