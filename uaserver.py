#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import sys
import SocketServer
import socket
import os
import uaclient
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class SmallSMILHandler(ContentHandler):

    def __init__(self):
        self.L_Primera = ['username', 'passwd']
        self.L_Segunda = ['ip', 'puerto']
        self.L_Tercera = ['puerto']
        self.L_Cuarta = ['ip', 'puerto']
        self.L_Quinta = ['path']
        self.L_Sexta = ['path']
        self.Lista = []

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


class EchoHandler(SocketServer.DatagramRequestHandler):
    """
    Echo server class
    """
    RTP = [0, '0']

    def handle(self):
        while 1:
            # Leyendo línea a línea lo que nos envía el proxy/User Agent
            line = self.rfile.read()
            # Si no hay más líneas salimos del bucle infinito
            if not line:
                break
            print 'Recibimos...\r\n' + line
            IP_Recib = self.client_address[0]
            Puerto_Recib = self.client_address[1]
            Linea0 = line.split('\r\n')
            Linea = Linea0[0].split(' ')
            Metodo = Linea[0]
            Lista_Metodos = ["Invite", "Bye", "Ack"]
            UserName = Lista[0]['username']
            uaclient.log(Lista[4]['path'], 'Recibir', IP_Recib, Puerto_Recib,
                         Linea0[0] + '\r\n')
            try:
                if len(Linea) != 3 or Linea[2] != 'SIP/2.0':
                    Envio = 'SIP/2.0 400 Bad Request\r\n\r\n'
                    self.wfile.write(Envio)
                    print 'Enviamos...\r\n' + Envio
                    Log = 'SIP/2.0 400 Bad Request\r\n'
                    uaclient.log(Lista[4]['path'], 'Enviar', IP_Recib,
                                 Puerto_Recib, Log)
                else:
                    if not Metodo in Lista_Metodos:
                        if line != '':
                            Envio = 'SIP/2.0 405 Method Not Allowed\r\n\r\n'
                            self.wfile.write(Envio)
                            print 'Enviamos...\r\n' + Envio
                            Log = 'SIP/2.0 405 Method Not Allowed\r\n'
                            uaclient.log(Lista[4]['path'], 'Envio', IP_Recib,
                                         Puerto_Recib, Log)
                    else:
                        if Metodo == 'Invite':
                            Info = line.split('\r\n\r\n')
                            SDP = Info[1].split('\r\n')
                            IP = SDP[1].split(' ')
                            self.RTP[0] = IP[3]
                            Puerto = SDP[4].split(' ')
                            self.RTP[1] = Puerto[3]
                            Envio = 'SIP/2.0 100 Trying\r\n\r\n'
                            Envio += 'SIP/2.0 180 Ringing\r\n\r\n'
                            Envio += 'SIP/2.0 200 OK\r\n'
                            Envio += 'Content-Type: application/sdp\r\n\r\n'
                            Envio += 'v = 0\r\no = ' + UserName + ' '
                            Envio += Lista[1]['ip'] + '\r\ns = misesion\r\n'
                            Envio += 't = 0\r\n' + 'm = audio '
                            Envio += Lista[2]['puerto'] + ' RTP\r\n\r\n'
                            print 'Enviamos...\r\n' + Envio
                            self.wfile.write(Envio)
                            uaclient.log(Lista[4]['path'], 'Enviar', IP_Recib,
                                         Puerto_Recib,
                                         'SIP/2.0 100 Trying\r\n')
                            uaclient.log(Lista[4]['path'], 'Enviar', IP_Recib,
                                         Puerto_Recib,
                                         'SIP/2.0 180 Ringing\r\n')
                            uaclient.log(Lista[4]['path'], 'Enviar', IP_Recib,
                                         Puerto_Recib,
                                         'SIP/2.0 200 OK\r\n')
                        elif Metodo == 'Ack':
                            print 'Envio RTP.....'
                            #aEjecutar es un string con lo que se ejecuta
                                #en la shell
                            aEjecutar = './mp32rtp -i ' + self.RTP[0] + ' -p '
                            aEjecutar += str(self.RTP[1]) + '< '
                            aEjecutar += Lista[5]['path']
                            print "Vamos a ejecutar", aEjecutar
                            os.system('chmod 755 mp32rtp')
                            os.system(aEjecutar)
                            uaclient.log(Lista[4]['path'], 'Enviar',
                                         self.RTP[0], self.RTP[1],
                                         'Envio RTP\r\n')
                            print 'Terminado RTP'
                        elif Metodo == 'Bye':
                            Envio = 'SIP/2.0 200 OK\r\n\r\n'
                            print 'Enviamos...\r\n' + Envio
                            self.wfile.write(Envio)
                            Log = 'SIP/2.0 200 OK\r\n'
                            uaclient.log(Lista[4]['path'], 'Enviar', IP_Recib,
                                         Puerto_Recib, Log)
                            uaclient.log(Lista[4]['path'], 'Finish', '', '',
                                         '')
            except socket.error:
                Texto = 'Error: No server listening at '
                Texto += IP_Recib + ' port ' + str(Puerto_Recib) + '\r\n'
                uaclient.log(Lista[4]['path'], 'Error', '', '', Texto)
                print Texto
                raise SystemExit

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    if len(sys.argv) == 2:
        if os.path.exists(sys.argv[1]):
            parser = make_parser()
            cHandler = SmallSMILHandler()
            parser.setContentHandler(cHandler)
            info_ua = sys.argv[1]
            parser.parse(open(info_ua))
            Lista = cHandler.get_tags()
            if Lista[1]['ip'] == '':
                Lista[1]['ip'] = '127.0.0.1'
            serv = SocketServer.UDPServer((Lista[1]['ip'], int(Lista[1]['puerto'])),
                                          EchoHandler)
            print "Listening..."
            serv.serve_forever()
        else:
            print 'El fichero no existe'
    else:
        print 'Usage: python uaserver.py config'
