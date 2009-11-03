""" stuff that can be used for both client and server """
import struct
import constants as const
from packet import DataPacket

def hash_company_password(password, server_unique_id, game_seed):
    """
    hash a company password
    @param         password: password to hash
    @type          password: string
    @param server_unique_id: unique id of the server
    @type  server_unique_id: hex string
    @param        game_seed: game seed to use
    @type         game_seed: int
    @returns:                hashed password
    @rtype:                  hex string
    """
    if len(password) == 0:
        return ""
    salted_pw = []
    for i in range(32):
        if len(password) > i:
            salted_pw.append(ord(password[i]))
        else:
            salted_pw.append(0)
        salted_pw[i] ^= ord(server_unique_id[i]) ^ (game_seed >> i) & 0xFF
    sp = "".join(map(chr, salted_pw))
    try:
        import hashlib
        m = hashlib.md5()
    except ImportError:
        import md5
        m = md5.new()
    m.update(sp)
    hashed_pw = m.hexdigest()
    return hashed_pw

def createPacketHeader(command, payload):
    """
    create a packet header for payload PAYLOAD
    @param payload: payload to create header for
    @type  payload: string
    @param command: packet type
    @type  command: uint8
    """
    return const.HEADER.pack(const.HEADER.size + len(payload), command)
def parsePacketHeader(header):
    """
    parse a packet header
    @param header: header to read
    @type  header: string >= 3 long
    @rtype:        tuple
    @returns:      (size, packettype)
    """
    return const.HEADER.unpack_from(header)

def complete_data_to_packet(data):
    size, command = parsePacketHeader(data)
    size -= const.HEADER_SIZE
    return DataPacket(size, command, data[const.HEADER_SIZE:])
def packet_to_complete_data(p):
    header = createPacketHeader(p.command, p.data)
    return header + p.data
    
class OTTDProtocol:
    """
    Protocol description for OpenTTD-python
    When subclassing, overwrite sendString(self, msg) for sending raw data, and overwrite packetReceived for processing incoming data
    @ivar recvd: internal incoming data buffer
    @type recvd: string
    """
    def stringReceived(self, msg):
        """
        Call this method whenever you want to process data. it calls the dataReceived method every time a whole packet is available
        @param msg: received data
        @type  msg: string
        """
        try:
            self.recvd += msg 
        except AttributeError:
            self.recvd = msg
        
        while len(self.recvd) >= const.PACKETSIZEHEADER_SIZE:
            size, = const.PACKETSIZEHEADER.unpack_from(self.recvd)
            if len(self.recvd) < size:
                break
            packet = self.recvd[:size]
            self.recvd = self.recvd[size:]
            self.dataReceived(packet)
    def dataReceived(self, data):
        """
        Call this method for whole packets in their raw form. It converts it into a DataPacket and calls PacketReceived with it.
        @param data: data to convert
        @type  data: string
        """
        self.packetReceived(complete_data_to_packet(data))
    def packetReceived(self, packet):
        """
        Overwrite this method to do something with the packet it.
        @param packet: the packet that was received
        @type  packet: DataPacket instance
        """
        pass #overwrite
    def sendString(self, msg):
        """
        Overwrite this method to send raw data somewhere, the extra arguments from sendData and sendPacket also get passed to here
        @param msg: the data to send
        @type  msg: string
        """
        pass #overwrite sending raw data
    def sendData(self, data, command, *arg):
        """
        convert data+command to raw data and call sendString with it, also pass other arguments to sendString
        @param    data: packet payload
        @type     data: string
        @param command: packet id for use in the header
        @type  command: int
        """
        self.sendString(createPacketHeader(command, data) + data, *arg)
    def sendPacket(self, packet, *arg):
        """
        convert DataPacket into payload and packetid and pass it to sendData, also passes optional arguments to sendData which passes it to sendString
        @param packet: packet to convert
        @type  packet: DataPacket instance
        """
        self.sendData(packet.data, packet.command, *arg)
    
    