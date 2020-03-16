#!/usr/bin/python2
#revision: 10-03-2020
import time
import RPi.GPIO as GPIO
import os
import threading
monitor12VPin = 18
backup12v= 06
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(monitor12VPin, GPIO.IN)
GPIO.setup(backup12v, GPIO.OUT)
#GPIO.setvarnings(False)
version="16-03-2020"
print("revision: "+version)

print("Reiniciando NTP service")
os.system("sudo service ntp restart")

def actualizar():
    print("Actualizando codigos")
    os.system("cd /transpubenza")
    os.system("git pull https://github.com/pauzuriaga/codigos-python-de-captura-de-fotos-raspberry.git")
    return

dia=time.strftime("%d")
print("Dia: "+dia)
if (dia == "10" or dia == "25"):    
    t = threading.Thread(target=actualizar)
    t.start()    
else:
    print("Hoy no hay actualizaciones pendientes.")
    print("Cada 10 y 25 de cada mes se consultaran actualizaciones")

try:
    while True: #Keep Monitoring continuosly
        time.sleep(1) # check the GPIO pin every other second
        if (GPIO.input(monitor12VPin)):  #si esta encendido
            GPIO.output(backup12v, True)
            print("Switche encendido")
        else: # Ignition Key is turned off
           time.sleep(28) # Sleep for 25 seconds to avoid accidental Ignition switch off and then check again
           if not (GPIO.input(monitor12VPin)): # If still off, then proceed with shutting down the system.
               print("Apagando...")
               time.sleep(2)
               os.system('shutdown -h now')
               GPIO.output(backup12v, False)
               GPIO.cleanup()
               #time.sleep(45)
               
           
except KeyboardInterrupt:
    GPIO.cleanup()
    print("gpio libres")
except NameError as e:
    GPIO.cleanup()
    print("gpio libres")
    print(e)
    print("Error inesperado:", sys.exc_info()[0])
finally:
    GPIO.cleanup()
    print("gpio libres")