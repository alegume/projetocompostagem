#!/usr/bin/python3
"""
@name: MQ-135.py - MQ-135 GAS SENSOR
@disclaimer: Copyright 2017, KRIPT4
@lastrelease: Dic 27 2017 16:50
"""

"""
MQ135 gas sensor | ADS1115 (Analog-to-Digital Converter for Raspberry Pi)

Datasheet can be found here: https://www.olimex.com/Products/Components/Sensors/SNS-MQ135/resources/SNS-MQ135.pdf

Application
They are used in air quality control equipments for buildings/offices, are suitable for detecting of NH3, NOx, alcohol, Benzene, smoke, CO2, etc

Original creator of this library: https://github.com/GeorgK/MQ135
"""

import sys
import math
import operator
import time
from datetime import datetime
import csv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import socket
import os
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Informacoes do host
dir_path = os.path.dirname(os.path.realpath(__file__))
hostname = socket.gethostname()

# Credenciais do Google Drive API
try:
	scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
	creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dir_path, 'secret_key.json'), scope)
	client = gspread.authorize(creds)
	# Abre uma o documeto (spreadsheet)
	spreadsheet = client.open(hostname)
except Exception as e:
		print(e)
		print('Erro ao conectar no google clound')

# Medis de Canoinhas retiradas de: https://pt.weatherspark.com/y/29811/Clima-caracter%C3%ADstico-em-Canoinhas-Brasil-durante-o-ano
t = 16 # assume current temperature. Recommended to measure with DHT22
h = 70 # assume current humidity. Recommended to measure with DHT22

"""
First version of an RaspBerryPi Library for the MQ135 gas sensor
TODO: Review the correction factor calculation. This currently relies on
the datasheet but the information there seems to be wrong.
"""

# The load resistance on the board
RLOAD = 10.0
# Calibration resistance at atmospheric CO2 level
RZERO = 76.63
# Parameters for calculating ppm of CO2 from sensor resistance
PARA = 116.6020682
PARB = 2.769034857

# Parameters to model temperature and humidity dependence
CORA = 0.00035
CORB = 0.02718
CORC = 1.39538
CORD = 0.0018
CORE = -0.003333333
CORF = -0.001923077
CORG = 1.130128205

# Atmospheric CO2 level for calibration purposes
# updated from: https://g1.globo.com/ciencia-e-saude/noticia/2019/04/06/concentracao-de-gas-carbonico-na-atmosfera-e-a-maior-em-3-milhoes-de-anos.ghtml
ATMOCO2 = 400

"""
@brief  Get the correction factor to correct for temperature and humidity

@param[in] t  The ambient air temperature
@param[in] h  The relative humidity

@return The calculated correction factor
"""

def getCorrectionFactor(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG):
	# Linearization of the temperature dependency curve under and above 20 degree C
	# below 20degC: fact = a * t * t - b * t - (h - 33) * d
	# above 20degC: fact = a * t + b * h + c
	# this assumes a linear dependency on humidity
	if t < 20:
		return CORA * t * t - CORB * t + CORC - (h-33.)*CORD
	else:
		return CORE * t + CORF * h + CORG

"""
@brief  Get the resistance of the sensor, ie. the measurement value

@return The sensor resistance in kOhm
"""

def getResistance(value_pin,RLOAD):
	return ((1023./value_pin) - 1.)*RLOAD

"""
@brief  Get the resistance of the sensor, ie. the measurement value corrected
        for temp/hum

@param[in] t  The ambient air temperature
@param[in] h  The relative humidity

@return The corrected sensor resistance kOhm
"""

def getCorrectedResistance(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD):
	return getResistance(value_pin,RLOAD) / getCorrectionFactor(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG)

"""
@brief  Get the ppm of CO2 sensed (assuming only CO2 in the air)

@return The ppm of CO2 in the air
"""

def getPPM(PARA,RZERO,PARB,value_pin,RLOAD):
	return PARA * math.pow((getResistance(value_pin,RLOAD)/RZERO), -PARB)

"""
@brief  Get the ppm of CO2 sensed (assuming only CO2 in the air), corrected
        for temp/hum

@param[in] t  The ambient air temperature
@param[in] h  The relative humidity

@return The ppm of CO2 in the air
"""

def getCorrectedPPM(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD,PARA,RZERO,PARB):
	return PARA * math.pow((getCorrectedResistance(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD)/RZERO), -PARB)

"""
@brief  Get the resistance RZero of the sensor for calibration purposes

@return The sensor resistance RZero in kOhm
"""

def getRZero(value_pin,RLOAD,ATMOCO2,PARA,PARB):
	return getResistance(value_pin,RLOAD) * math.pow((ATMOCO2/PARA), (1./PARB))

"""
@brief  Get the corrected resistance RZero of the sensor for calibration
        purposes

@param[in] t  The ambient air temperature
@param[in] h  The relative humidity

@return The corrected sensor resistance RZero in kOhm
"""

def getCorrectedRZero(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD,ATMOCO2,PARA,PARB):
	return getCorrectedResistance(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD) * math.pow((ATMOCO2/PARA), (1./PARB))

"""
Re-maps a number from one range to another. That is, a value of fromLow would get mapped to toLow,
a value of fromHigh to toHigh, values in-between to values in-between, etc.

# Arduino: (0 a 1023)
# Raspberry Pi: (0 a 26690)

More Info: https://www.arduino.cc/reference/en/language/functions/math/map/
"""

def map(x,in_min,in_max,out_min,out_max):
	return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def log_local(data):
	try:
		with open(os.path.join(dir_path, 'logs-gases', 'logs-gas-135-A.csv'), 'a') as f:
			w = csv.writer(f)
			w.writerow(data)
	except Exception as e:
		print(e)
		print('Erro ao salvar dado em arquivo .csv')

def log_nuvem(data):
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
	planilha = 'A-sensor-135'
	for ws in ws_list:
		if ws.title == planilha:
			worksheet = spreadsheet.worksheet(planilha)
			break
	# Se nao existe, cria
	if worksheet == None:
		worksheet = spreadsheet.add_worksheet(title=planilha, rows='100', cols='2')
		worksheet.append_row(['Data Hora', 'Valor (PPM)', 'ppm', 'resistance', 'Correted RZero', 'RZero'])
	# Escreve
	try:
		worksheet.append_row(data)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados para a nuvem')


def main():
	# Create the I2C bus
	i2c = busio.I2C(board.SCL, board.SDA)
	# Create the ADC object using the I2C bus
	ads = ADS.ADS1015(i2c)
	###### Create single-ended input on channel 1
	chan = AnalogIn(ads, ADS.P1)
	#print("{:>5}\t{:>5.3f}".format(chan.value, chan.voltage))

	value_ads = chan.value # value obtained by ADS1115
	value_pin = map((value_ads - 565), 0, 26690, 0, 1023) # 565 / 535 fix value
	rzero = getRZero(value_pin,RLOAD,ATMOCO2,PARA,PARB)
	correctedRZero = getCorrectedRZero(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD,ATMOCO2,PARA,PARB)
	resistance = getResistance(value_pin,RLOAD)
	ppm = getPPM(PARA,RZERO,PARB,value_pin,RLOAD)
	correctedPPM = getCorrectedPPM(t,h,CORA,CORB,CORC,CORD,CORE,CORF,CORG,value_pin,RLOAD,PARA,RZERO,PARB)

	#print("\n MQ135 Gas Sensor:\n")
	#print("\t MQ135 RZero: %s" % round(rzero))
	#print("\t Corrected RZero: %s" % round(correctedRZero))
	#print("\t Resistance: %s" % round(resistance))
	#print("\t PPM: %s" % round(ppm))
	#print("\t Corrected PPM: %s ppm" % round(correctedPPM))

	# data hora,
	data = [datetime.now().strftime('%d/%m/%Y %H:%M:%-S'), round(correctedPPM), round(ppm), round(resistance), round(correctedRZero), round(rzero)]

	# Modificacoes
	try:
		log_local(data)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados locais')
	try:
		log_nuvem(data)
	except Exception as e:
		print(e)
		print('Erro ao enviar dados na nuvem')


if __name__ == "__main__":
	main()
