import socket
import networking
import select
import constants as const
import date
from datastorageclass import DataStorageClass
from packet import DataPacket
import os

M_NONE = 0
M_TCP  = 1 << 0
M_UDP  = 1 << 1
M_BOTH = M_TCP | M_UDP # this is already in client.py


class BaseServerTCPClient(object, networking.OTTDProtocol):
    """
    TCP Client handler class for everything, you can subclass it to make it more specific
    """
    def __init__(self, clientsocket, addr, server):
        """
        initializer for TCP Client handler
        @param clientsocket: socket to use
        @type  clientsocket: socket instance
        @param         addr: (ip, port) tuple with connection source
        @type          addr: tuple
        @param       server: Server that accepted the connection
        @type        server: BaseServer instance
        """
        self.socket = clientsocket
        self.addr   = addr
        self.p_buff = ""
        self.connected = True
        self.server = server
        print "connected to %s:%d" % addr
    def fileno(self):
        """
        Used for wrapping the socket to select.select()
        @return: socket fileno
        @rtype:  int
        """
        return self.socket.fileno()
    def close_connection(self, msg):
        """
        Set a connection to closed, display a message and close the socket
        @param msg: message to show
        @type  msg: string
        """
        self.connected = False
        print "connection closed: %s" % msg
        self.socket.close()
    def recv_data(self):
        """
        Receive data from the socket and call stringReceived with the data
        """
        try:
            data = self.socket.recv(4096)
        except socket.error, e:
            self.close_connection("error: %s" % e)
            return
        if len(data) == 0:
            self.close_connection("without error")
            return
        self.stringReceived(data)
    def sendString(self, msg):
        """
        Send a string to the socket, called by sendData
        @param msg: data to send
        @type  msg: string
        """
        try:
            self.socket.send(msg)
        except socket.error, e:
            self.close_connection("error: %s" % e)
    def packetReceived(self, p):
        """
        Called when a full packet is received
        @param p: packet
        @type  p: DataPacket instance
        """
        pass #overwrite
    def send_data(self):
        """
        Called every 0.1 seconds to send stuff over the socket
        """
        pass

class BaseServer(object):
    """
    OpenTTD server - can be used for game, content and master
    @cvar connectiontype: the protocols the server should serve
    @type connectiontype: bitwise enum int
    @cvar tcp_client_handler: the BaseServerTCPClient client to use for handling tcp connections
    @type tcp_client_handler: class
    @ivar readsocks: socks it needs to select from
    @type readsocks: list
    @ivar writesocks: socks it needs to write to
    @type writesocks: list
    @ivar clients: list of connected clients
    @type clients: list
    @ivar server_udp_sock: udp socket(if available)
    @type server_udp_sock: socket
    @ivar server_tcp_sock: tcp listening socket(if available)
    @type server_tcp_sock: socket
    """
    connectiontype = M_NONE
    tcp_client_handler = BaseServerTCPClient
    def __init__(self, host='', port=3979):
        """
        init method for BaseServer
        @param host: address the server should bind to
        @type  host: str
        @param port: port the server should bind to
        @type  port: int
        """
        self.readsocks = []
        self.writesocks = []
        self.clients = []
        if self.connectiontype & M_UDP:
            self.server_udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.server_udp_sock.bind((host, port))
            self.readsocks.append(self.server_udp_sock)
        if self.connectiontype & M_TCP:
            self.server_tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_tcp_sock.bind((host, port))
            self.server_tcp_sock.listen(5)
            self.readsocks.append(self.server_tcp_sock)
    def serve_forever(self):
        """
        Main loop, loops forever
        """
        while 1:
            self.accept()
    def accept(self):
        """
        Read once from a socket, and write to all - main method
        """
        r, w, e = select.select(self.readsocks, [], [], 0.1)
        for s in r:
            if self.connectiontype & M_UDP and s is self.server_udp_sock:
                self.handle_udp_message(*s.recvfrom(4096))
            if self.connectiontype & M_TCP and s is self.server_tcp_sock:
                self.handle_tcp_connection(*s.accept())
            if self.connectiontype & M_TCP and type(s) is self.tcp_client_handler:
                s.recv_data()
                if not s.connected:
                    self.handle_client_quit(s)
        for s in self.writesocks:
            if self.connectiontype & M_TCP and type(s) is self.tcp_client_handler and s.connected:
                s.send_data()
                if not s.connected:
                    self.handle_client_quit(s)
        self.send_data()
    def send_data(self):
        """
        Called every 0.1 seconds
        """
        pass #overwrite
    def handle_udp_message(self, data, addr):
        """
        Handles incoming udp messages and translates it to packets
        @param data: data to handle
        @type  data: bytes
        @param addr: source of the message(ip, port)
        @type  addr: tuple(str, int)
        """
        p = networking.complete_data_to_packet(data)
        p.source = addr
        self.handle_udp_packet(p)
    def handle_udp_packet(self, p):
        """
        Gets called when an udp packet is received
        @param p: the packet
        @type  p: DataPacket instance
        """
        pass #overwrite
    def handle_tcp_connection(self, sock, addr):
        """
        Gets called when a new tcp connection is made
        @param sock: connection socket
        @type  sock: socket instance
        @param addr: address (ip, port)
        @type  addr: tuple(str, int)
        """
        client = self.tcp_client_handler(sock, addr, self)
        self.readsocks.append(client)
        self.writesocks.append(client)
        self.clients.append(client)
    def broadcast_packet(self, p):
        """
        Send a packet to all clients
        @param p: the packet to send
        @type  p: DataPacket instance
        """
        for c in self.clients:
            c.sendPacket(p)
    def handle_client_quit(self, c):
        """
        Called when a client quits
        @param c: quitting client
        @type  c: BaseServerTCPClient instance
        """
        self.readsocks.remove(c)
        self.writesocks.remove(c)
        self.clients.remove(c)
       


