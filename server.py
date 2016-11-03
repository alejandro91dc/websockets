#!/usr/bin/env python
# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys

from twisted.internet import ssl, protocol, task, defer
from twisted.python import log
from twisted.python.modules import getModule
from twisted.internet import protocol, reactor, endpoints

class Echo(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)

def main(reactor):
    log.startLogging(sys.stdout)
    certData = getModule(__name__).filePath.sibling('rootCA.pem').getContent()
    authData = getModule(__name__).filePath.sibling('server.pem').getContent()
    authority = ssl.Certificate.loadPEM(certData)
    certificate = ssl.PrivateCertificate.loadPEM(authData)
    factory = protocol.Factory.forProtocol(Echo)
    reactor.listenSSL(8080, factory, certificate.options(authority))
    return defer.Deferred()

if __name__ == '__main__':
    task.react(main)
