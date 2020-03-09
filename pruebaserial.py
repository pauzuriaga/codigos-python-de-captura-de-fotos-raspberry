#!/usr/bin/python2
# -*- coding: utf-8 -*-
#revision: 03/12/2019
import serial
import time
import os
import requests
import threading
import sys
import cv2
import base64
import RPi.GPIO as GPIO

monitor12VPin = 18

GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(monitor12VPin, GPIO.IN)

url = 'http://179.50.12.201/transpubenza/sgcf/api/gps/trama'
arduino = serial.Serial("/dev/ttyS0", 9600, timeout = 3.0)
txt=''
trama=''
print("revision: 03/12/2019")
os.system("sudo service ntp restart")
def Envio(datos,url,intentos):
    cont = intentos
    try:
        time.sleep(0.5)
        print("enviando...")
        res = requests.post(url, json=datos, auth=('pablo', '123'))
        while(res.json()['status'] != "ok" and cont<30):
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

def codificar(img,fechapiloto,horapiloto):
    codificado, buffer = cv2.imencode('.png', img)
    if codificado:
        im64 = base64.b64encode(buffer).decode('utf-8')
        url = 'http://179.50.12.201/transpubenza/sgcf/api/gps/foto'
        datos = {'foto':im64, 'orden':orden, 'fecha':fechapiloto,'hora':horapiloto,'tipo':5}
        t = threading.Thread(target=Envio, args=(datos,url,0))
        t.start()
    else:
        print("Error al codificar")
        codificar(img,fechapiloto,horapiloto)
    return

def fotoPiloto():
    if not orden==0:
        fechapiloto= time.strftime("%y-%m-%d")
        horapiloto = time.strftime("%H-%M-%S")
        nombre = '/home/pi/transpubenza/DVR/Piloto/'+str(orden)+'_'+str(fechapiloto)+'_'+str(horapiloto)+'_piloto.png'
        print("foto piloto()")
        cmd= 'ffmpeg -s 640x480 -i /dev/v4l/by-path/platform-3f980000.usb-usb-0:1.2:1.0-video-index0 -ss 0:0:2 -frames 1 ' + nombre
        os.system(cmd)

        img = cv2.imread(nombre, 0)
        img1 = cv2.resize(img, None, fx=0.4, fy=0.4)
        codificar(img1,fechapiloto,horapiloto)
    return
def reiniciar():
    os.system('reboot')
    return
def closeBrowser():
    os.system('pkill chromium')
    return
def tiempos(t1,t2, carro):
    os.system('sudo espeak -ves+f3 -s 165 -a 100 -k 30 --stdout " Vehículo '+carro+', tu espacio de tiempo hacia adelante es de' + t1 + ' minutos, y hacia atrás es de '+ t2 +' minutos" | aplay')
    return
def mensaje(msj, carro):
    os.system('sudo espeak -ves+f3 -s 165 -a 100 -k 30 --stdout " Vehículo '+carro+','+ msj+'" | aplay')
    return
def enviarTrama(query):
    try:
        #socket.gethostbyname('google.com')
        #c = socket.create_connection(('google.com', 80), 1)
        #if c:        
        res = requests.post(url, json=query, auth=('pablo', '123'))
        if res:
            print ("Conectado")
            print(res.text)
            #evento=res.read().decode()
            evento=res.json()['evento']
            evento=int(evento)
            print(evento)
            if evento==2:
                t = threading.Thread(target=closeBrowser, args=())
                t.start()
            if evento==1:
                reiniciar()
            if evento==3:
                #print("evento 3")
                t = threading.Thread(target=fotoPiloto, args=())
                t.start()
                #fotoPiloto()
            if evento==4:
                mensaje=res.json()['msj']
                t = threading.Thread(target=mensaje, args=(mensaje, carro))
                t.start()
        else:
            print("Error de red")
            
        #c.close()
    except requests.exceptions.Timeout:
        print ("timeout")
    except requests.exceptions.HTTPError:
        print ("HTTP")
    except requests.exceptions.ConnectionError:
        print ("Connection error")
    except requests.exceptions.TooManyRedirects:
        print ("Too many redirections")
    except KeyboardInterrupt:
        print("keyboard")
    except ValueError:
        print("valueError inesperado:", sys.exc_info()[0])        
    return

try:
    while True:
        fechaServidor= time.strftime("%y-%m-%d")
        fecha= time.strftime("%d-%m-%y")
        
        fechatrama= time.strftime("%d%m%y")
        horatrama = time.strftime("%H%M%S")
        #var = raw_input("Introducir un Comando: ")
        #arduino.write(var)
        time.sleep(0.1)
        if (GPIO.input(monitor12VPin)):
            #print("encendido")    
            pass        
        else:
            print("apagado")
        while arduino.inWaiting() > 0:
            try:
                txt += arduino.readline()
                print (txt)
                trama = txt
                #txt = ''
                if len(trama)>10:
                    try:
                        fechaArd,carro,conteoTorniquete,conteoAdelante,conteoAtras,puertaAdelante,puertaAtras,estadoReg,estadoSenAdelante,estadoSenAtras,estadoGPS,curso,velocidad,precision,latitud,longitud = trama.split(" ")
                    except ValueError as e:
                        print("valueError inesperado:", sys.exc_info()[0])
                    idtrama = ''+str(carro)+str(fechatrama)+str(horatrama)
                    hora = time.strftime("%H%M%S")
                    #print(idtrama)
                    orden=carro
                    if (GPIO.input(monitor12VPin)):
                        estadoGPS=1
                    else:
                        estadoGPS=0
                    query = {
                    "orden": carro,
                    "idTrama": idtrama,
                    "electromecanica": conteoTorniquete,
                    "adelante": conteoAdelante,
                    "atras": conteoAtras,
                    "puertaadelante": puertaAdelante,
                    "puertaatras": puertaAtras,
                    "estadoReg": estadoReg,
                    "estadoSenAde": estadoSenAdelante,
                    "estadoSenAtr": estadoSenAtras,
                    "estado": estadoGPS,
                    "latitud": latitud,
                    "longitud": longitud,
                    "direccion": curso,
                    "velocidad": velocidad,
                    "precision": precision,
                    "fecha": fechaServidor,
                    "hora": hora                
                    }
                    print(fechaArd)
                    t = threading.Thread(target=enviarTrama, args=([query]))
                    t.start()
                    #enviarTrama(query)
                    time.sleep(1)
                    trama = ''
                    if len(fechaArd)==8:
                        if fecha==fechaArd:
                            print("fechas iguales")
                            arduino.write(fecha+'-ok-0\n')
                            #arduino.write('13-06-19'+'-no-0\n')
                            #arduino.write(fecha+"-")
                        else:
                            print("fechas distintas")
                            print(fecha)
                            #time.sleep(0.5)
                            arduino.write(fecha+'-no-0\n')
                    txt = '' 
            except ValueError as e:
                print("valueError inesperado:", sys.exc_info()[0])
                        
    arduino.close()
except KeyboardInterrupt:
    arduino.close()
    print("serial cerrado")
except ValueError:
    print("valueError inesperado:", sys.exc_info()[0]) 
except NameError as e:
    #arduino.close()
    print("Error inesperado:", sys.exc_info()[0])
    pass


