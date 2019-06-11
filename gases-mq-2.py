#!/usr/bin/python3

import time
from GasDetection.gas_detection import GasDetection

def main():
	print('Calibrando ...')
	detection = GasDetection()

	try:
		while True:
			ppm = detection.percentage()

			print('CO: {} ppm'.format(ppm[detection.CO_GAS]))
			print('H2: {} ppm'.format(ppm[detection.H2_GAS]))
			print('CH4: {} ppm'.format(ppm[detection.CH4_GAS]))
			print('LPG: {} ppm'.format(ppm[detection.LPG_GAS]))
			print('PROPANO: {} ppm'.format(ppm[detection.PROPANE_GAS]))
			print('ÁLCOOL: {} ppm'.format(ppm[detection.ALCOHOL_GAS]))
			print('FUMAÇA: {} ppm\n'.format(ppm[detection.SMOKE_GAS]))

			time.sleep(0.25)

	except KeyboardInterrupt:
		print('\nUsuário abortou o processo =/')

if __name__ == '__main__':
	main()
