# Projeto Compostagem IFSC

Projeto para monitorar os processos de compostagem utilizando Raspberry PI, múltiplos sensores de temperatura e de gases. O projeto está em desenvolvimento no IFSC de Canoinhas.


## Dados em tempo real
https://docs.google.com/spreadsheets/d/1N5u85N-EJNjbe2gtfyZ38t3KWcYSQklyatBzgI10Ji0/


## Conversor ADC ADS1115

### Conectar

    ADS1x15 VDD -> Raspberry Pi 3.3V
    ADS1x15 GND -> Raspberry Pi GND
    ADS1x15 SCL -> Raspberry Pi SCL
    ADS1x15 SDA -> Raspberry Pi SDA

### Instalar biblioteca Adafruit

  `sudo pip3 install adafruit-circuitpython-ads1x15`
  
Referência: https://github.com/adafruit/Adafruit_CircuitPython_ADS1x15


## Sensor de gases MQ-2

O sensor MQ-2 pode detectar vários gases (CO, H2, CH4, GLP, propano, álcool, fumaça) e gera tensão analógica. Este projeto pode convertê-lo em digital usando ADS1015 ou ADS1115 e filtrar os gases. O sensor pode ser impreciso, portanto, não use essas medidas se você precisar delas para fins de segurança. Use algum dispositivo de medição profissional, se você precisar fazer isso.

### Clonar repositório de detecção de gases
    git clone https://github.com/filips123/GasDetection.git

Referência: https://github.com/filips123/GasDetection


## Sensor de gases MQ-135

### Conectar

    VCC: 5V
    GND: GND
    D0: Saída Digital
    A0: Saída Analógica

Referências: 

https://github.com/KRIPT4/MQ135-ADS1115-Python

https://portal.vidadesilicio.com.br/sensor-de-gas-mq-135/

## Sensor de temperatura


### Importante

Ligar um resistor de 4.7kohm (~5kohm segundo a documentação) entre: 1) alimentação, 2) sensor e 3) input de dados


### Passos

1. At the command prompt, enter: sudo nano /boot/config.txt, then add this to the bottom of the file:

  `dtoverlay=w1-gpio`

2. Reiniciar (sudo reboot)

3. Verificar módulos (sudo modprobe w1-gpio)

4. Verificar módulos (sudo modprobe w1-therm)

5. Mudar diretório (cd /sys/bus/w1/devices)

6. Listar dispositivos (ls):

7. Entrar nos diretórios(cd 28-XXXXXXXXXXXX)

8. Ver temperatura (cat w1_slave)


Fonte: http://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/

