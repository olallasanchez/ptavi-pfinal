#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sys
import os
import socket
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

fichero = sys.argv[1]


def log(Fichero, Evento, IP, Puerto, Texto):
    Log = open(Fichero, 'a')
    if Evento == 'Enviar':
        Log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) +
                  ' Send to ' + str(IP) + ':' + str(Puerto) + ': ' +
                  Texto)
    elif Evento == 'Recibir':
        Log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) +
                  ' Received from ' + str(IP) + ':' + str(Puerto) +
                  ': ' + Texto)
    elif Evento == 'Error':
        Log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) + ' '
                  + Texto)
    elif Evento == 'Finish':
        Log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) +
                  ' Finishing...\r\n')
    elif Evento == 'Start':
        Log.write(time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime()) +
                  ' Starting...\r\n')
    Log.close()


class SmallSMILHandler(ContentHandler):
    def __init__(self):
        self.L_Primera = ['username', 'passwd']
        self.L_Segunda = ['ip', 'puerto']
        self.L_Tercera = ['puerto']
        self.L_Cuarta = ['ip', 'puerto']
        self.L_Quinta = ['path']
        self.L_Sexta = ['path']
        self.Lista = []

    #Despues de haber creafdo una lista general,
        #creado un diccionario con cada atributo
    def startElement(self, name, attrs):

        if name == 'account':
            dic = {"name": "acount"}
            for atributo in self.L_Primera:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)
        elif name == 'uaserver':
            dic = {"name": "uaserver"}
            for atributo in self.L_Segunda:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)
        elif name == 'rtpaudio':
            dic = {"name": "rtpaudio"}
            for atributo in self.L_Tercera:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)
        elif name == 'regproxy':
            dic = {"name": "regproxy"}
            for atributo in self.L_Cuarta:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)
        elif name == 'log':
            dic = {"name": "log"}
            for atributo in self.L_Quinta:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)
        elif name == 'audio':
            dic = {"name": "audio"}
            for atributo in self.L_Sexta:
                dic[atributo] = attrs.get(atributo, "")
            self.Lista.append(dic)

    def get_tags(self):
        return self.Lista


if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if len(sys.argv) == 4:
        if os.path.exists(sys.argv[1]):
            parser = make_parser()
            cHandler = SmallSMILHandler()
            parser.setContentHandler(cHandler)
            fichero = sys.argv[1]
            parser.parse(open(fichero))
            Lista = cHandler.get_tags()
            if Lista[1]['ip'] == '':
                Lista[1]['ip'] = '127.0.0.1'
            PROXY = Lista[3]['ip']
            PORT_PX = int(Lista[3]['puerto'])
            # Creamos el socket del Proxy
            my_proxy = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            my_proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_proxy.connect((PROXY, PORT_PX))

            UserName = Lista[0]['username']
            Metodo = sys.argv[2]
            Metodo = Metodo[0].upper() + Metodo[1:].lower()
            if Metodo == 'Register':
                log(Lista[4]['path'], 'Start', '', '', '')
                Line = 'Register sip:' + UserName + ':'
                Line += Lista[1]['puerto'] + ' SIP/2.0\r\n' + 'Expires: '
                Line += sys.argv[3] + '\r\n\r\n'
                Log = 'Register sip:' + UserName + ':'
                Log += Lista[1]['puerto'] + ' SIP/2.0\r\n'
                log(Lista[4]['path'], 'Enviar', PROXY, PORT_PX, Log)
            elif Metodo == 'Invite':
                Line = 'Invite sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                Line += 'Content-Type: application/sdp\r\n\r\n'
                Line += 'v = 0\r\no = ' + UserName + ' ' + Lista[1]['ip']
                Line += '\r\ns = misesion\r\n' + 't = 0\r\n' + 'm = audio '
                Line += Lista[2]['puerto'] + ' RTP\r\n\r\n'
                Log = 'Invite sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                log(Lista[4]['path'], 'Enviar', PROXY, PORT_PX, Log)
            elif Metodo == 'Bye':
                Line = 'Bye sip:' + sys.argv[3] + ' SIP/2.0\r\n\r\n'
                Log = 'Bye sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                log(Lista[4]['path'], 'Enviar', PROXY, PORT_PX, Log)
            try:
                # Contenido que vamos a enviar
                my_proxy.send(Line)
                data0 = my_proxy.recv(1024)
                print 'Enviamos...\r\n' + Line
                print 'Recibimos...\r\n' + data0
                data = data0.split('\r\n')
                if data[0] == 'SIP/2.0 200 OK' and Metodo == 'Bye':
                    log(Lista[4]['path'], 'Finish', '', '', '')
                else:
                    log(Lista[4]['path'], 'Recibir', PROXY, PORT_PX,
                        data[0] + '\r\n')
            except socket.error:
                Texto = 'Error: No server listening at '
                Texto += PROXY + ' port ' + str(PORT_PX) + '\r\n'
                log(Lista[4]['path'], 'Error', '', '', Texto)
                print Texto
                raise SystemExit

            processed_data = data0.split('\r\n')
            #Modifico la comprobación del mensaje del servidor y
                #añado la escucha habilitando un buffer
            if processed_data[0] == "SIP/2.0 100 Trying" and \
               processed_data[2] == "SIP/2.0 180 Ringing" and \
               processed_data[4] == "SIP/2.0 200 OK":
                log(Lista[4]['path'], 'Recibir', PROXY, PORT_PX,
                    "SIP/2.0 180 Ringing\r\n")
                log(Lista[4]['path'], 'Recibir', PROXY, PORT_PX,
                    "SIP/2.0 200 OK\r\n")
                LINE = 'Ack sip:' + sys.argv[3] + ' SIP/2.0\r\n\r\n'
                print 'Enviamos...\r\n' + LINE
                my_proxy.send(LINE)
                Log = 'Ack sip:' + sys.argv[3] + ' SIP/2.0\r\n'
                log(Lista[4]['path'], 'Enviar', PROXY, PORT_PX, Log)
                IP = processed_data[8].split(' ')
                IP = IP[3]
                Puerto = processed_data[11].split(' ')
                Puerto = str(Puerto[3])
                print 'Envio RTP.....'
                #aEjecutar es un string con lo que se ejecuta en la shell
                aEjecutar = './mp32rtp -i ' + IP + ' -p ' + Puerto + '< '
                aEjecutar += Lista[5]['path']
                print "Vamos a ejecutar", aEjecutar
                os.system('chmod 755 mp32rtp')
                os.system(aEjecutar)
                log(Lista[4]['path'], 'Enviar', Lista[1]['ip'],
                    Lista[2]['puerto'], 'Envio RTP\r\n')
                print 'Terminado RTP'
            my_proxy.close()

        else:
            print 'El fichero no existe'
    else:
        print 'Usage: python uaclient.py config method option'
