#!/usr/bin/python2
#16-12-2019
import RPi.GPIO as GPIO
import cv2
import time
import sys
import base64
import threading
import requests
from config import (orden)

print("revision: 16/12/2019")
print(orden)

global camAtras
global camAdelante
global tipo
camAtras = cv2.VideoCapture("/dev/v4l/by-path/platform-3f980000.usb-usb-0:1.1.2:1.0-video-index0")
camAdelante = cv2.VideoCapture("/dev/v4l/by-path/platform-3f980000.usb-usb-0:1.1.3:1.0-video-index0")

adelante = 26
atras = 21
obsadelante = 19
obsatras = 20
obsreg = 16

GPIO.setmode(GPIO.BCM)
GPIO.setup(atras,GPIO.IN)
GPIO.setup(adelante,GPIO.IN)
GPIO.setup(obsadelante,GPIO.IN)
GPIO.setup(obsatras,GPIO.IN)
GPIO.setup(obsreg,GPIO.IN)

def Envio(datos,url,intentos):
    cont = intentos
    try:
        time.sleep(0.5)
        print("enviando...")
        res = requests.post(url, json=datos, auth=('pablo', '123'))
        while(res.json()['status'] != "ok" and cont<60):
            cont = cont+1
            Envio(datos,url,cont)
            #print(res.json()['status'])
        print(res.json()['status'])
    except requests.exceptions.Timeout:
        print ("timeout")
        time.sleep(1)
        cont = cont+1
        Envio(datos,url,cont)
    except requests.exceptions.HTTPError:
        print ("HTTP")
        time.sleep(1)
        cont = cont+1
        Envio(datos,url,cont)
    except requests.exceptions.ConnectionError:
        print ("Connection error")
        time.sleep(1.5)
        cont = cont+1
        Envio(datos,url,cont)
    except requests.exceptions.TooManyRedirects:
        print ("Too many redirections")
        time.sleep(1)
        cont = cont+1
        Envio(datos,url,cont)
    return

def codificar(img,tipo):
    codificado, buffer = cv2.imencode('.png', img)
    if codificado:
        im64 = base64.b64encode(buffer).decode('utf-8')
        url = 'http://179.50.12.201/transpubenza/sgcf/api/gps/foto'
        datos = {'foto':im64, 'orden':orden, 'fecha':fecha,'hora':horaEnvio,'tipo':tipo}

        t = threading.Thread(target=Envio, args=(datos,url,0))
        t.start()
    else:
        print("Error al codificar")
        codificar(img,tipo)
    return

def FotoAtras(i,frame):
    print("fotoAtras()")
    #camAtras = cv2.VideoCapture(2)
    if i=="conteo":        
        nombre = '/home/pi/transpubenza/DVR/FotosAtras/'+str(orden)+'_'+str(fecha)+'_'+str(hora)+'_camAtras.png'
        print("ruta:"+nombre)
        tipo=3
    else:
        nombre = '/home/pi/transpubenza/DVR/ObstruccionAtras/'+str(orden)+'_'+str(fecha)+'_'+str(hora)+'_camAtras.png'   
        print("ruta:"+nombre)
        tipo=4
    time.sleep(0.05)
    #leido, frame = camAtras.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.resize(frame, None, fx=0.4, fy=0.4)
    cv2.imwrite(nombre, frame)
    codificar(frame,tipo)
    
def FotoAdelante(i,frame):
    print("fotoAdelante()")
    #camAdelante = cv2.VideoCapture(0)
    if i=="conteo":
        nombre = '/home/pi/transpubenza/DVR/FotosAdelante/'+str(orden)+'_'+str(fecha)+'_'+str(hora)+'_camAdelante.png'
        print("ruta:"+nombre)
        tipo=1
    else:
        nombre = '/home/pi/transpubenza/DVR/ObstruccionAdelante/'+str(orden)+'_'+str(fecha)+'_'+str(hora)+'_camAdelante.png'
        print("ruta:"+nombre)
        tipo=2
    time.sleep(0.05)
    #leido, frame = camAdelante.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame = cv2.resize(frame, None, fx=0.4, fy=0.4)
    cv2.imwrite(nombre, frame)
    codificar(frame,tipo)
    
try:
    while True: #Keep Monitoring continuosly
        fecha= time.strftime("%y-%m-%d")
        hora = time.strftime("%H-%M-%S")
        horaEnvio = time.strftime("%H%M%S")
        leidoAd, frameAdelante = camAdelante.read()
        leidoAt, frameAtras = camAtras.read()
        if (GPIO.input(atras)): # pulso atras
            FotoAtras("conteo",frameAtras)
        if (GPIO.input(adelante)): # pulso adelante
            FotoAdelante("conteo",frameAdelante)        
            #aqui iria la obs de registradora
        if (GPIO.input(obsatras)): # pulso obsatras
            FotoAtras("obstruccion",frameAtras)
        if (GPIO.input(obsadelante)): # pulso obsadelante
            FotoAdelante("obstruccion",frameAdelante)
        #camAtras.release()
        #camAdelante.release()
        time.sleep(0.05)
except KeyboardInterrupt:
    camAtras.release()
    camAdelante.release()
    GPIO.cleanup()
    print("camaras liberada keyboard")
except NameError as e:
    print (e)
    print("Error inesperado:", sys.exc_info()[0])
except ValueError as e:
    print (e)
    print("Error inesperado:", sys.exc_info()[0])
    
