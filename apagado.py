#!/usr/bin/python2
#revision: 26/08/2019
import time
import RPi.GPIO as GPIO
import os
monitor12VPin = 18
backup12v= 06
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(monitor12VPin, GPIO.IN)
GPIO.setup(backup12v, GPIO.OUT)
#GPIO.setvarnings(False)

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