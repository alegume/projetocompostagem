# Projeto Compostagem IFSC


## Dados em tempo real
https://docs.google.com/spreadsheets/d/1N5u85N-EJNjbe2gtfyZ38t3KWcYSQklyatBzgI10Ji0/


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

8. VEr temperatura (cat w1_slave)


Fonte: http://www.circuitbasics.com/raspberry-pi-ds18b20-temperature-sensor-tutorial/

