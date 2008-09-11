#!/bin/env python
# made by thomas in 5 hours - no guarantees ;)
import sys, struct
import logging, logging.config
import threading
import socket
import random
import time
import string
import os, os.path
import math
import copy
import traceback
import StringIO
import datetime
from operator import itemgetter
from struct_zerostrings import *
from ottd_constants import *
import signal

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

logging.config.fileConfig('logging.cfg')
#logging.basicConfig(level=logging.DEBUG, format='%(name)s: %(message)s', filename='ottd_lib.log', filemode='w')
#logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger()

#connection modes
M_TCP=1 
M_UDP=2
M_BOTH=3

class DataStorageClass:
    __dict__ = {}
    def __getitem__(self, key):
        return self.__dict__[key]
    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            raise AttributeError
    def __setattr__(self, key, value):
        if not key == "__dict__":
            self.__dict__[key] = value
    def __delattr__(self, key):
        del self.__dict__[key]
    def getDict(self):
        return self.__dict__

class DataPacket:
    size=0
    command=0
    data=0
    offset=0
    def __init__(self, size, command, data):
        self.size = size
        self.command = command
        self.data = data
        self.offset = 0
    def recv_something(self, type):
        """
        This method gets something from the data and returns it as array
        @param type: string containing types needed to unpack
        @type  type: string
        @rtype:      array
        @returns:    array with unpacked stuff
        """
        ret, size = unpackFromExt(type, self.data[self.offset:])
        self.offset += size
        return ret
    def recv_str(self):
        return self.recv_something('z')[0]
    def recv_uint8(self):
        return self.recv_something('B')[0]
    def recv_uint16(self):
        return self.recv_something('H')[0]
    def recv_uint32(self):
        return self.recv_something('I')[0]
    def recv_uint64(self):
        return self.recv_something('Q')[0]
    def recv_bool(self):
        return self.recv_something('B')[0] == 1

class Client(threading.Thread):
    socket_udp = None
    socket_tcp = None
    errors = []
    
    def __init__(self, ip, port, debugLevel=0, uid=None):
        self.ip = ip
        self.port = port
        self.debuglevel=debugLevel
        self.uid=uid
        
        LOG.debug('__init__')
        self.running = True # sighandler will change this value
        self.lock = threading.Lock()
        threading.Thread.__init__(self)
        
    def disconnect(self):
        if not self.socket_tcp is None:
            LOG.debug('closing TCP socket')
            self.socket_tcp.close()
        if not self.socket_udp is None:
            LOG.debug('closing UDP socket')
            self.socket_udp.close()
        self.socket_tcp = None
        self.socket_udp = None
        self.running = False
    
    def connect(self, mode=M_BOTH):
        try:
            self.connectionmode = mode
            LOG.debug('creating sockets')
            
            if mode in [M_TCP, M_BOTH]:
                self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_tcp.settimeout(5)
            if mode in [M_UDP, M_BOTH]:
                self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        
                self.socket_udp.settimeout(5)
            
            try:
                self.ip = socket.gethostbyaddr(self.ip)[2][0]
            except:
                pass
            LOG.debug("connecting to %s:%d" % (self.ip, self.port))
            
            LOG.debug('connecting to server')
            if mode in [M_TCP, M_BOTH]:
                self.socket_tcp.connect((self.ip, self.port))
            if mode in [M_UDP, M_BOTH]:
                self.socket_udp.connect((self.ip, self.port))
            
            self.running = True
            #self.getGameInfo()
            
            #self.throwRandomData()
            #self.packetTest()
            #self.sendMsg(PACKET_UDP_CLIENT_FIND_SERVER,type=M_UDP)
            #self.sendRaw(self.packetTest())
            #data=self.receiveMsg_UDP()
            
            LOG.debug( "connect finished" )
            return True
        except Exception, e:
            LOG.error('receiveMsg_UDP error: '+str(e))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            LOG.error(errorMsg.getvalue())
            if not str(e) in self.errors:
                self.errors.append(str(e))
            return False
    
    def run(self):
        #overwrite
        pass

    def getServerList(self):
        payload_size = struct.calcsize("B")
        payload = struct.pack("B", NETWORK_MASTER_SERVER_VERSION)
        self.sendMsg(PACKET_UDP_CLIENT_GET_LIST, payload_size, payload, type=M_UDP)
        size, command, content = self.receiveMsg_UDP()
        #print "short:", struct.calcsize("H")
        if command == PACKET_UDP_MASTER_RESPONSE_LIST:
            offset = 0
            #print "BUFFER: \n%s" % (content[offset:offset+4].encode("hex"))
            [protocol_version], size = unpackFromExt('B', content[offset:])
            offset += size

            #print "BUFFER: \n%s" % (content[offset:offset+struct.calcsize("B")].encode("hex"))
            [number], size = unpackFromExt('H', content[offset:])
            offset += size
            if protocol_version == 1:
                servers = []
                LOG.debug("protocol version %d" % protocol_version)
                LOG.debug("master server knows %d servers:" % number)
                for i in range(0, number):
                    [ip, port], size = unpackFromExt('4sH', content[offset:])
                    offset += size
                    servers.append((socket.inet_ntoa(ip), port))
                    LOG.debug(" %s:%d" % (socket.inet_ntoa(ip), port))
                return servers
            else:
                LOG.debug("unkown protocol version %d" % protocol_version)
        return None

    
    def getGRFInfo(self, grfs):
        payload_size = struct.calcsize("B")
        payload = struct.pack("B", len(grfs))
        for grf in grfs:
            payload += packExt('4s16s', grf[0], grf[1])
            payload_size += struct.calcsize('4s16s')
        self.sendMsg(PACKET_UDP_CLIENT_GET_NEWGRFS, payload_size, payload, type=M_UDP)
        result = self.receiveMsg_UDP()
        if result is None:
            LOG.debug("unable to receive UDP packet")
            return None
        newgrfs = []
        size, command, content = result
        if command == PACKET_UDP_SERVER_NEWGRFS:
            offset = 0
            [reply_count], size = unpackFromExt('B', content[offset:])
            offset += size
            for i in range(0, reply_count):
                [grfid, md5sum], size = unpackFromExt('4s16s', content[offset:])
                offset += size
                
                [grfname], size = unpackFromExt('z', content[offset:])
                offset += size
                
                newgrfs.append([grfid, md5sum, grfname])
            LOG.debug("installed grfs:")
            for grf in newgrfs:
                LOG.debug(" %s - %s - %s" % (grf[0].encode("hex"), grf[1].encode("hex"), grf[2]))
            return newgrfs
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_GET_NEWGRFS: %d" % (command))

    def getCompanyInfo(self):
        self.sendMsg(PACKET_UDP_CLIENT_DETAIL_INFO, type=M_UDP)
        res = self.receiveMsg_UDP()
        if res is None:
            return None
        size, command, content = res
        if command == PACKET_UDP_SERVER_DETAIL_INFO:
            offset = 0
            [info_version, player_count], size = unpackFromExt('BB', content[offset:])
            offset += size
            if info_version == NETWORK_COMPANY_INFO_VERSION or info_version == 4: # 4 = old version (pre rev 13712):
                companies = []
                
                for i in range(0, player_count):
                    op = copy.copy(offset)
                    company = DataStorageClass()
                    [
                        company.number, 
                        company.company_name, 
                        company.inaugurated_year, 
                        company.company_value, 
                        company.money, 
                        company.income, 
                        company.performance, 
                        company.password_protected,
                    ], size = unpackFromExt('=BzIqqqHB', content[offset:], debug=False)
                    offset += size
                    
                    company.vehicles, size = unpackFromExt('H'*5, content[offset:], debug=False)
                    offset += size
                    
                    company.stations, size = unpackFromExt('H'*5, content[offset:], debug=False)
                    offset += size
                    
                    # version4 has much more information, but we will ignore those ...
                    
                    companies.append(company)
                return companies
            else:
                LOG.error("unsupported NETWORK_COMPANY_INFO_VERSION: %d. supported version: %d" % (info_version, NETWORK_COMPANY_INFO_VERSION))
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_DETAIL_INFO: %d" % (command))
    def getTCPCompanyInfo(self):
        self.sendMsg(PACKET_CLIENT_COMPANY_INFO, type=M_TCP)
        res = self.receiveMsg_TCP()
        if res is None:
            return None
        size, command, content = res
        if command == PACKET_SERVER_COMPANY_INFO:
            packet = DataPacket(size, command, content)
            [info_version, player_count] = packet.recv_something('BB')
            if info_version == NETWORK_COMPANY_INFO_VERSION or info_version == 4: #4 and 5 are the same:
                companies = []
                firsttime = True
                for i in range(0, player_count):
                    if not firsttime:
                        res2 = self.receiveMsg_TCP()
                        if res2 is None:
                            return None
                        size, command, content = res
                        packet = DataPacket(size, command, content)
                        [info_version, player_count] = packet.recv_something('BB')
                    firsttime = False
                    
                    company.index = packet.recv_uint8()
                    company.name = packet.recv_str()
                    company.startyear = packet.recv_uint32()
                    company.value = packet.recv_uint64()
                    company.money = packet.recv_uint64()
                    company.income = packet.recv_uint64()
                    company.performance = packet.recv_uint16()
                    
                    company.passworded = packet.recv_bool()
                    
                    company.vehicles = []
                    for j in range(0,4):
                        company.vehicles.append(packet.recv_uint16)
                    company.stations = []
                    for j in range(0,4):
                        company.stations.append(packet.recv_uint16)
                    company.players = packet.recv_str()
                    companies.append(company)
        else:
            LOG.error("unexpected reply on PACKET_CLIENT_COMPANY_INFO: %d" % (command))
    
    def getShortGameInfo(self):
        # stripped down version of getGameInfo()
        self.sendMsg(PACKET_UDP_CLIENT_FIND_SERVER, type=M_UDP)
        result = self.receiveMsg_UDP()
        if result is None:
            LOG.debug("unable to receive UDP packet")
            return None
        size, command, content = result
        if command == PACKET_UDP_SERVER_RESPONSE:
            offset = 0
            [command2], size = unpackFromExt('B', content, offset)
            offset += size
            
            if command2 == NETWORK_GAME_INFO_VERSION:
                [grfcount], size = unpackFromExt('B', content, offset)
                offset += size

                info = DataStorageClass()
                info.grfs = []
                if grfcount != 0:
                    for i in range(0, grfcount):
                        [grfid, md5sum], size = unpackFromExt('4s16s', content[offset:])
                        offset += size
                # the grf stuff is still wrong :|
                [
                    info.game_date,
                    start_date,
                    info.companies_max,
                    info.companies_on,
                    info.spectators_max,
                    server_name,
                    server_revision,
                    server_lang,
                    info.use_password,
                    info.clients_max,
                    info.clients_on,
                    info.spectators_on,
                    map_name,
                    map_width,
                    map_height,
                    map_set,
                    dedicated,
                ], size = unpackExt('IIBBBzzBBBBBzHHBB', content[offset:])
                #LOG.debug("got Game Info (%d byes long)\n"%(size))
                return info
            else:
                LOG.debug("> old gameinfo version detected: %d" % command2)
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_FIND_SERVER: %d" % (command))
    
    def getGameInfo_old(self, encode_grfs=False):
        self.sendMsg(PACKET_UDP_CLIENT_FIND_SERVER, type=M_UDP)
        result = self.receiveMsg_UDP()
        if result is None:
            LOG.debug("unable to receive UDP packet")
            return None
        size, command, content = result
        if command == PACKET_UDP_SERVER_RESPONSE:
            offset = 0
            [command2], size = unpackFromExt('B', content, offset)
            offset += size
            
            if command2 == NETWORK_GAME_INFO_VERSION:
                [grfcount], size = unpackFromExt('B', content, offset)
                offset += size

                info = DataStorageClass()
                info.grfs = []
                if grfcount != 0:
                    for i in range(0, grfcount):
                        [grfid, md5sum], size = unpackFromExt('4s16s', content[offset:])
                        offset += size
                        if encode_grfs:
                            info.grfs.append((grfid.encode('hex'), md5sum.encode('hex')))
                        else:
                            info.grfs.append((grfid, md5sum))
                # the grf stuff is still wrong :|
                [
                    info.game_date,
                    info.start_date,
                    info.companies_max,
                    info.companies_on,
                    info.spectators_max,
                    info.server_name,
                    info.server_revision,
                    info.server_lang,
                    info.use_password,
                    info.clients_max,
                    info.clients_on,
                    info.spectators_on,
                    info.map_name,
                    info.map_width,
                    info.map_height,
                    info.map_set,
                    info.dedicated,
                ], size = unpackExt('IIBBBzzBBBBBzHHBB', content[offset:])
                #LOG.debug("got Game Info (%d byes long)\n"%(size))
                return info
            else:
                LOG.debug("> old gameinfo version detected: %d" % command2)
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_FIND_SERVER: %d" % (command))
    def getGameInfo(self, encode_grfs=False, short=False):
        self.sendMsg(PACKET_UDP_CLIENT_FIND_SERVER, type=M_UDP)
        result = self.receiveMsg_UDP()
        if result is None:
            LOG.debug("unable to receive UDP packet")
            return None
        size, command, content = result
        p = DataPacket(size, command, content)
        
        info = DataStorageClass()
        info.game_info_version = p.recv_uint8()
        
        if info.game_info_version >= 4:
            grfcount = p.recv_uint8()
            grfs = []
            
            for i in range(0, grfcount):
                [grfid, md5sum] = p.recv_something('4s16s')
                if encode_grfs:
                    grfs.append((grfid.encode('hex'), md5sum.encode('hex')))
                else:
                    grfs.append((grfid, md5sum))
            if not short:
                info.grfs = grfs
        if info.game_info_version >=3:
            info.game_date  = p.recv_uint32()
            if not short:
                info.start_date = p.recv_uint32()
            else:
                p.recv_uint32()
        if info.game_info_version >=2:
            info.companies_max  = p.recv_uint8()
            info.companies_on   = p.recv_uint8()
            info.spectators_max = p.recv_uint8()
        if info.game_info_version >=1:
            info.server_name     = p.recv_str()
            if not short:
                info.server_revision = p.recv_str()
            else:
                p.recv_str()
            info.server_lang     = p.recv_uint8()
            info.use_password    = p.recv_bool()
            info.clients_max     = p.recv_uint8()
            info.clients_on      = p.recv_uint8()
            info.spectators_on   = p.recv_uint8()
            if info.game_info_version < 3: # 16-bit dates were removed from version 3
                info.game_date  = p.recv_uint16() + DAYS_TILL_ORIGINAL_BASE_YEAR
                if not short:
                    info.start_date = p.recv_uint16() + DAYS_TILL_ORIGINAL_BASE_YEAR
                else:
                    p.recv_uint16()
            if not short:
                info.map_name       = p.recv_str()
                info.map_width      = p.recv_uint16()
                info.map_height     = p.recv_uint16()
                info.map_set        = p.recv_uint8()
                info.dedicated      = p.recv_bool()
            else:
                p.recv_something("zHBB")
        return info
    def throwRandomData(self):
        rsize = 128
        rand = str(random.getrandbits(rsize))
        res = struct.pack("%ds"%rsize, rand)
        LOG.debug(" fuzzing with %d bytes: '%s'" % (rsize, rand))
        for i in range(0,127):
            self.sendMsg(i, rsize, res, type=M_UDP)
            #size, command, content = self.receiveMsg_UDP()
            #print "received: ", i, size, command
        
        
        
    def sendRaw(self, data, type=0):
        if type == M_TCP and self.socket_tcp is None:
            LOG.debug('cannot send: TCP not connected!')
            return
        if type == M_UDP and self.socket_udp is None:
            LOG.debug('cannot send: UDP not connected!')
            return
        try:
            if type == M_TCP:
                self.socket_tcp.send(data)
            elif type == M_UDP:
                self.socket_udp.send(data)
        except Exception, e:
            LOG.debug('sendMsg error: '+str(e))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            LOG.error(errorMsg.getvalue())
            

    def packetTest(self):
        # h = short, 2 bytes, packet size
        # c = 1 byte, packet command
        # 15C = 15 char, server revision
        # 80c = 80 char, network player name
        # c, 1 byte, play as number
        # c, 1 byte, NETLANG (language)
        # 33c, 33 char, unique id
        size = 2+1+15+80+1+1+33
        serverversion = "revision1234567"
        playername = "nickname".rjust(80)
        playas = 1
        netlang = 0
        uniqueid = "foobar".rjust(33)
        
        format_payload = '15s80sbb33s'
        payload_size = struct.calcsize(format_payload)
        payload = struct.pack(format_payload, serverversion, playername, playas, netlang, uniqueid)
        
        self.sendMsg(PACKET_CLIENT_JOIN, payload_size, payload)

        
    def sendMsg(self, command, payloadsize=0, payload=None, type=M_UDP):
        header_format = 'hb'
        header_size= struct.calcsize(header_format)
        #print "sizes: %d + %d = %d" % (header_size, payloadsize, header_size+payloadsize)
        header = struct.pack(header_format, header_size+payloadsize, command)
        if payloadsize > 0:
            self.sendRaw(header+payload, type)
        else:
            self.sendRaw(header, type)
        
    def receiveMsg_UDP(self):
        try:
            if self.socket_udp is None:
                return None
            headerformat = 'hb'
            headersize = struct.calcsize(headerformat)
            data = self.socket_udp.recv(4096)
            #print data
            [size, command], osize = unpackFromExt('hb', data, 0)
            LOG.debug("received size: %d/%d, command: %d"% (size, osize, command))
            content = data[headersize:]
            
            return size, command, content
        except Exception, e:
            LOG.error('receiveMsg_UDP error: '+str(e))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            logging.error(errorMsg.getvalue())
            if not str(e) in self.errors:
                self.errors.append(str(e))

    def receiveMsg_TCP(self):
        if self.socket_tcp is None:
            return None
        note = ""
        headersize = struct.calcsize('hb')
        #print "headersize: ", headersize
        data = ""
        readcounter = 0
        #LOG.debug( "receiving...")
        while len(data) < headersize:
            data += self.socket_tcp.recv(headersize-len(data))
        if readcounter > 1:
            note += "HEADER SEGMENTED INTO %s SEGMENTS!" % readcounter
        
        (size, command) = struct.unpack('hb', data)
        if not command in [PACKET_SERVER_FRAME, PACKET_SERVER_SYNC]:
            if command in packet_names.keys():
                LOG.debug("received size: %d, command: %s (%d)"% (size, packet_names[command], command))
            else:
                LOG.debug("received size: %d, command: %d"% (size, command))
        size -= headersize # remove size of the header ...
        data = ""
        readcounter = 0
        while len(data) < size and self.running:
            readcounter+=1
            data += self.socket_tcp.recv(size-len(data))
            #print "waiting on ", size - len(data)
        if readcounter > 1:
            note += "DATA SEGMENTED INTO %s SEGMENTS!" % readcounter
        
        if not self.running:
            return None
        
        return size, command, data
        #content = struct.unpack(str(size) + 's', data)
        #content = content[0]

        #LOG.debug(size, command, content)
    def dateToYMD(self, date):
        is_leap = lambda y: ((y%400) == 0 or ((y%100) != 0 and (y%4) == 0))
        after_feb = lambda d: (d.month > 2 or (d.month == 2 and d.day > 28))
        ymddate = datetime.date.fromordinal(date)
        ymddate = datetime.date.fromordinal(date-(365, 366)[is_leap(ymddate.year) and after_feb(ymddate)])
        return (ymddate.year, ymddate.month, ymddate.day)

        
