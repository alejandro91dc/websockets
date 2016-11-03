#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys
import txaio
import json
import os
from twisted.internet import ssl, protocol, task, defer
from twisted.python import log
from twisted.python.modules import getModule
from twisted.internet import protocol, reactor, endpoints
from twisted.web.server import Site
from twisted.web.static import File
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol, listenWS 
import Classes

class EchoServerProtocol(WebSocketServerProtocol):
    def onMessage(self, payload, isBinary):
        folder = json.loads(payload.decode('utf8'))
        if "type" in folder and folder['type'] == 'newF':
            object = Classes.newF(folder['name'], folder['privilege'], folder['path'])
            os.system("echo 'include = /etc/samba/conf."+object.name+"' | sudo tee --append /etc/samba/smb.conf")    
            os.system("echo '["+object.name+"]\n read only = "+object.privilege+"\n path= "+object.path+"' | sudo tee --append /etc/samba/conf."+object.name)

        if "type" in folder and folder['type'] == 'delF':
            object = Classes.delF(folder['name'], folder['privilege'], folder['path'])
            os.system("sudo sed -i '/"+object.name+"/d' /etc/samba/smb.conf" )
            os.system("sudo rm /etc/samba/conf."+object.name)
            
        self.sendMessage(payload, isBinary)
        

def main(reactor):
    log.startLogging(sys.stdout)
    certData = getModule(__name__).filePath.sibling('rootCA.pem').getContent()
    authData = getModule(__name__).filePath.sibling('server.pem').getContent()
    authority = ssl.Certificate.loadPEM(certData)
    certificate = ssl.PrivateCertificate.loadPEM(authData)

    factory = WebSocketServerFactory(u"wss://127.0.0.1:9000")
    factory.setProtocolOptions(
        allowedOrigins=[
            "https://127.0.0.1:8080",
            "https://localhost:8080",
            "https://10.10.2.99:8000",
            "https://10.10.2.93:8080",
            "https://10.10.2.99:8080",
        ]
    )

    factory.protocol = EchoServerProtocol
    listenWS(factory, certificate.options())

    webdir = File(".")
    webdir.contentTypes['.crt'] = 'application/x-x509-ca-cert'
    web = Site(webdir)
    reactor.listenSSL(8080, web, certificate.options(authority))

    return defer.Deferred()

if __name__ == '__main__':

    task.react(main)
