#######################
# Dennis MUD          #
# telnet.py           #
# Copyright 2018-2021 #
# Michael D. Reiley   #
#######################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

# Parts of codebase borrowed from https://github.com/TKeesh/WebSocketChat

import traceback

from lib.logger import Logger

from twisted.internet import protocol
from twisted.protocols.basic import LineReceiver
from twisted.conch.telnet import (
    IAC,
    NOP,
    LINEMODE,
    GA,
    WILL,
    DONT,
    DO,
    SB,
    SE,
    NAWS,
    WONT,
    ECHO,
    NULL,
    MODE,
    LINEMODE_EDIT,
    LINEMODE_TRAPSIG,
)

from lib.mccp import *
import zlib

# negotiations for v1 and v2 of the protocol
MCCP = bytes([86])  # b"\x56"
MCCP2 = b"\x56"
MSSP = bytes([70])  # b"\x46"
MSSP_VAR = bytes([1])  # b"\x01"
MSSP_VAL = bytes([2])  # b"\x02"
#MSSP = b"\x46"
#MSSP_VAR = b"\x01"
#MSSP_VAL = b"\x02"
FLUSH = zlib.Z_SYNC_FLUSH

def mssp_payload(config):
    # Payload of MSSP data should respect:
    # https://mudhalla.net/tintin/protocols/mssp/
    mssp_table = config["mssp_info"]
    varlist = b""
    for variable, value in mssp_table.items():
            varlist += (
                MSSP_VAR + bytes(str(variable), "utf-8") + MSSP_VAL + bytes(str(value), "utf-8")
            )
    payload = IAC+SB+MSSP+varlist+IAC+SE
    return payload

def mccp_compress(protocol, data):
    # MCCP zlib and IAC commands should respect:
    # https://mudhalla.net/tintin/protocols/mccp/
    """
    Handles zlib compression, if applicable.

    Args:
        data (str): Incoming data to compress.

    Returns:
        stream (binary): Zlib-compressed data.

    """
    if hasattr(protocol, "zlib"):
        return protocol.zlib.compress(data) + protocol.zlib.flush(FLUSH)
    return data

# Read the motd file.
try:
    with open("motd.telnet.txt") as f:
        motd = f.read()
except:
    motd = None


class ServerProtocol(LineReceiver):
    def __init__(self, factory):
        self.factory = factory
        self.peer = None
        # Protocol flags for later.
        self.protocol_flags = {
            "ENCODING": "utf-8",
            "SCREENREADER": False,
            "MSSP": False,
            "MCCP": False
        }
        self._log = Logger("telnet")
        self.mccp = False

    def connectionMade(self):
        p = self.transport.getPeer()
        self.peer = p.host + ':' + str(p.port)
        self.factory.register(self)
        
        #self.mccp=False
        # MCCP start
        #if self.mccp==False:
        #    mccpstart=IAC+WILL+MCCP2
        #    self.factory.communicate(self.peer, mccpstart, cmd=True)
        #    self._log.info("Sending MCCP offer to: {peer}", peer=self.peer)
        # MCCP end
        
        self._log.info("Client connected: {peer}", peer=self.peer)
        if motd:
            self.factory.communicate(self.peer, motd.encode('utf-8'))
        # MSSP stats
        msspstart=IAC+WILL+MSSP
        self.factory.communicate(self.peer, msspstart, cmd=True)
        self._log.info("Sending MSSP offer to: {peer}", peer=self.peer)
        # MSSP end

    def connectionLost(self, reason):
        self.factory.unregister(self)
        self._log.info("Client disconnected: {peer}", peer=self.peer)

    def lineReceived(self, line):
        # Don't log passwords.
        #print(line)
        # MSSP request
        if IAC+DONT+MSSP in line:
            self._log.info("{peer} doesnt want MSSP so leave it alone.", peer=self.peer)
            line=line.strip(IAC+DONT+MSSP)
        if IAC+DO+MSSP in line:
            self._log.info("{peer} wants some stats on mssp! Sending it now.", peer=self.peer)
            # Discard the command so the rest of the line still gets interpreted.
            line=line.strip(IAC+DO+MSSP)
            mssppayload = mssp_payload(self._config)
            self.factory.communicate(self.peer, mssppayload, cmd=True)
        # MSSP request end
        
        # MCCP start
        #if IAC+DO+MCCP2 in line:
        #    print("Client accepting to get mccp!")
        #    self.mccp = True
        #    self.zlib = zlib.compressobj(9)
        #    startmccp = IAC+SB+ MCCP2+ IAC+ SE
        #    self.factory.communicate(self.peer, startmccp, cmd=True)
        
        #if IAC+DONT+MCCP2 in line:
        #    print("Client wants to turn off mccp!")
        #    if hasattr(self, "zlib"):
        #        del self.zlib
        #    self.mccp = False
        #    stopmccp = IAC+SB+ MCCP2+ IAC+ SE
        #    self.factory.communicate(self.peer, startmccp, cmd=True)
        # MCCP end
        
        passcheck = line.split(b' ')
        if passcheck[0] == b'login' and len(passcheck) > 2:
            passcheck = b' '.join(passcheck[:2] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        elif passcheck[0] == b'register' and len(passcheck) > 2:
            passcheck = b' '.join(passcheck[:2] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        elif passcheck[0] == b'password' and len(passcheck) > 1:
            passcheck = b' '.join(passcheck[:1] + [b'********'])
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=passcheck)
        else:
            self._log.info("Client {peer} sending message: {line}", peer=self.peer, line=line)

        # Try to decode the line.
        try:
            line = line.decode('utf-8')
        except:
            self._log.info("Discarded garbage line from {peer}", peer=self.peer)
            return

        # Did we receive the quit pseudo-command?
        if line == "quit":
            self.factory.communicate(self.peer, "Goodbye for now.".encode('utf-8'))
            self.transport.loseConnection()
            return

        # Run the command while handling errors.
        try:
            self.factory.router.shell.command(self.factory.router[self.peer]["console"], line)
        except:
            self.factory.communicate(self.peer, traceback.format_exc().encode('utf-8'))
            self._log.error(traceback.format_exc())


class ServerFactory(protocol.Factory):

    def __init__(self, router, *args, **kwargs):
        self.router = router
        self.router.telnet_factory = self
        super(ServerFactory, self).__init__(*args)
        self.clients = []

    def buildProtocol(self, addr):
        return ServerProtocol(self)

    def register(self, client):
        self.clients.append({'client-peer': client.peer, 'client': client})
        self.router.register(client.peer, "telnet")

    def unregister(self, client):
        self.router.unregister(client.peer)
        for c in self.clients:
            if c['client-peer'] == client.peer:
                self.clients.remove(c)

    def communicate(self, peer, payload, cmd=False, mccpe=False):
        client = None
        for c in self.clients:
            if c['client-peer'] == peer:
                client = c['client']
        if client:
            #mccpe=client.mccp
            # Telnet wants a CRLF instead of just an LF. Some clients require this to display properly.
            #if mccpe: 
            #    payload = mccp_compress(client,payload)
            #    client.sendLine(payload)
            if cmd: 
                client.sendLine(payload)
            else: 
                client.sendLine(payload.decode('utf-8').replace('\n', '\r\n').encode('utf-8'))
