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
from log import LOG

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

#connection modes
M_NONE = 0
M_TCP  = 1 
M_UDP  = 2
M_BOTH = 3

class DataStorageClass(object):
    def __init__(self, dict={}):
        self.__dict__ = dict
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
    def __init__(self, size, command, data=""):
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
    def send_something(self, type, something):
        buf = packExt(type, *something)
        self.size += len(buf)
        self.data += buf
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
    def send_str(self, str):
        return self.send_something('z', [str])
    def send_uint8(self, i):
        return self.send_something('B', [i])
    def send_uint16(self, i):
        return self.send_something('H', [i])
    def send_uint32(self, i):
        return self.send_something('I', [i])
    def send_uint64(self, i):
        return self.send_something('Q', [i])
    def send_bool(self, b):
        if b:
            i = 1
        else:
            i = 0
        return self.send_something('B', [i])

class Client(threading.Thread):
    header_format = "hb"
    header_size   = struct.calcsize("hb")
    def __init__(self, ip, port, debugLevel=0, uid=None):
        self.socket_udp = None
        self.socket_tcp = None
        self.errors     = []
        self.connectionmode = M_NONE
        self.ip         = ip
        self.port       = port
        self.debuglevel = debugLevel
        self.uid        = uid
        
        LOG.debug('__init__')
        self.running    = True # sighandler will change this value
        self.lock       = threading.Lock()
        threading.Thread.__init__(self)
        
    def connect(self, mode=M_BOTH):
        try:
            LOG.debug('creating sockets')
            
            if mode & M_TCP:
                self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket_tcp.settimeout(5)
            if mode & M_UDP:
                self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        
                self.socket_udp.settimeout(5)
            
            try:
                self.ip = socket.gethostbyaddr(self.ip)[2][0]
            except Exception, e:
                LOG.error('gethost error on ip %s: %s'%(str(self.ip), str(e)))
                if not str(e) in self.errors:
                    self.errors.append(str(e))
                return False
                
            LOG.info("connecting to %s:%d" % (self.ip, self.port))
            
            if mode & M_TCP:
                self.socket_tcp.connect((self.ip, self.port))
            if mode & M_UDP:
                self.socket_udp.connect((self.ip, self.port))
            
            self.connectionmode |= mode
            self.running = True
            #self.getGameInfo()
            
            #self.throwRandomData()
            #self.packetTest()
            #self.sendMsg_UDP(PACKET_UDP_CLIENT_FIND_SERVER)
            #self.sendRaw(self.packetTest())
            #data=self.receiveMsg_UDP()
            
            LOG.debug( "connect finished" )
            return True
        except socket.error, e:
            LOG.error('connect error: %d (%s)' % (e[0], e[1]))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            LOG.error(errorMsg.getvalue())
            if not str(e) in self.errors:
                self.errors.append(str(e))
            return False
    def disconnect(self, mode=M_BOTH):
        if not self.socket_tcp is None and mode & M_TCP:
            LOG.debug('closing TCP socket')
            self.socket_tcp.close()
            self.socket_tcp = None
        if not self.socket_udp is None and mode & M_UDP:
            LOG.debug('closing UDP socket')
            self.socket_udp.close()
            self.socket_udp = None
        self.connectionmode &= ~mode
        if self.connectionmode == M_NONE:
            self.running = False
    def run(self):
        #overwrite
        pass

    def getServerList(self):
        payload = struct.pack("B", NETWORK_MASTER_SERVER_VERSION)
        self.sendMsg_UDP(PACKET_UDP_CLIENT_GET_LIST, payload)
        size, command, content = self.receiveMsg_UDP()
        if command == PACKET_UDP_MASTER_RESPONSE_LIST:
            p = DataPacket(size, command, content)
            protocol_version = p.recv_uint8()
            
            if protocol_version == 1:
                number = p.recv_uint16()
                servers = []
                LOG.debug("got response from master server with %d servers:" % number)
                for i in range(0, number):
                    [ip, port] = p.recv_something('4sH')
                    ip = socket.inet_ntoa(ip)
                    servers.append((ip, port))
                    LOG.debug(" %s:%d" % (ip, port))
                return servers
            else:
                LOG.debug("got unknown protocol version in response from master server %d" % protocol_version)
                return None

    
    def getGRFInfo(self, grfs):
        p = DataPacket(0, PACKET_UDP_CLIENT_GET_NEWGRFS)
        p.send_uint8(len(grfs))
        for grf in grfs:
            p.send_something('4s16s', grf)
        self.sendMsg_UDP(p.command, p.data)
        res = self.receiveMsg_UDP()
        if res is None:
            LOG.debug("unable to receive UDP packet")
            return None
        newgrfs = []
        p = DataPacket(*res)
        if p.command == PACKET_UDP_SERVER_NEWGRFS:
            reply_count = p.recv_uint8()
            for i in range(0, reply_count):
                [grfid, md5sum] = p.recv_something('4s16s')
                grfname = p.recv_str()
                newgrfs.append([grfid, md5sum, grfname])

            LOG.debug("Got reply to grf request with %d grfs:" % reply_count)
            for grf in newgrfs:
                LOG.debug(" %s - %s - %s" % (grf[0].encode("hex"), grf[1].encode("hex"), grf[2]))
            
            return newgrfs
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_GET_NEWGRFS: %d" % (p.command))

    def getCompanyInfo(self):
        self.sendMsg_UDP(PACKET_UDP_CLIENT_DETAIL_INFO)
        res = self.receiveMsg_UDP()
        if res is None:
            return None
        p = DataPacket(*res)
        if p.command == PACKET_UDP_SERVER_DETAIL_INFO:
            info_version = p.recv_uint8()
            player_count = p.recv_uint8()
            
            if info_version == NETWORK_COMPANY_INFO_VERSION or info_version == 4:
                companies = []
                
                for i in range(0, player_count):
                    company = DataStorageClass()
                    
                    company.number = p.recv_uint8()
                    company.company_name     = p.recv_str()
                    company.inaugurated_year = p.recv_uint32()
                    company.company_value    = p.recv_uint64()
                    company.money            = p.recv_uint64()
                    company.income           = p.recv_uint64()
                    company.performance      = p.recv_uint16()
                    company.password_protected = p.recv_bool()
                    company.vehicles = p.recv_something('H'*5)
                    company.stations = p.recv_something('H'*5)
                    
                    if info_version == 4:
                        # get the client information from version 4
                        players = []
                        while p.recv_bool():
                            player = DataStorageClass()
                            player.client_name = p.recv_str()
                            player.unique_id   = p.recv_str()
                            player.join_date   = p.recv_uint32()
                            players.append(player)
                        company.clients = players
                    
                    companies.append(company)
                
                if info_version == 4:
                    # get the list of spectators from version 4
                    players = []
                    while p.recv_bool():
                        player = DataStorageClass()
                        player.client_name = p.recv_str()
                        player.unique_id   = p.recv_str()
                        player.join_date   = p.recv_uint32()
                        players.append(player)
                        
                ret = DataStorageClass()
                ret.info_version = info_version
                ret.player_count = player_count
                ret.companies    = companies
                if info_version == 4:
                    ret.spectators = players
                return ret
            else:
                LOG.error("unsupported NETWORK_COMPANY_INFO_VERSION: %d. supported version: %d" % (info_version, NETWORK_COMPANY_INFO_VERSION))
        else:
            LOG.error("unexpected reply on PACKET_UDP_CLIENT_DETAIL_INFO: %d" % (command))
    def getTCPCompanyInfo(self):
        self.sendMsg_TCP(PACKET_CLIENT_COMPANY_INFO)
        res = self.receiveMsg_TCP()
        if res is None:
            return None
        size, command, content = res
        if command == PACKET_SERVER_COMPANY_INFO:
            p = DataPacket(size, command, content)
            [info_version, player_count] = p.recv_something('BB')
            if info_version == NETWORK_COMPANY_INFO_VERSION or info_version == 4: #4 and 5 are the same:
                companies = []
                firsttime = True
                for i in range(0, player_count):
                    if not firsttime:
                        res2 = self.receiveMsg_TCP()
                        if res2 is None:
                            return None
                        p = DataPacket(*res2)
                        if p.command != PACKET_SERVER_COMPANY_INFO:
                            LOG.error("unexpectged reply on PACKET_CLIENT_COMPANY_INFO: %d" % p.command)
                            return None
                        [info_version, player_count] = p.recv_something('BB')
                    firsttime = False
                    
                    company = DataStorageClass()
                    company.number           = p.recv_uint8() + 1
                    company.company_name     = p.recv_str()
                    company.inaugurated_year = p.recv_uint32()
                    company.company_value    = p.recv_uint64()
                    company.money            = p.recv_uint64()
                    company.income           = p.recv_uint64()
                    company.performance      = p.recv_uint16()
                    company.password_protected = p.recv_bool()
                    company.vehicles         = p.recv_something('H'*5)
                    company.stations         = p.recv_something('H'*5)
                    company.players          = p.recv_str()
                    companies.append(company)
                return companies
            else:
                LOG.error("unknown company info version %d, supported: %d" % (info_version, NETWORK_COMPANY_INFO_VERSION))
        else:
            LOG.error("unexpected reply on PACKET_CLIENT_COMPANY_INFO: %d" % (command))
    
    def getGameInfo(self, encode_grfs=False, short=False):
        self.sendMsg_UDP(PACKET_UDP_CLIENT_FIND_SERVER)
        result = self.receiveMsg_UDP()
        if result is None:
            LOG.debug("unable to receive UDP packet")
            return None
        size, command, content = result
        return self.processGameInfoResponse(size, command, content)
    def processGameInfoResponse(self, size, command, content, encode_grfs=False, short=False):
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
            self.sendMsg_UDP(i, res)
            #size, command, content = self.receiveMsg_UDP()
            #print "received: ", i, size, command
        
        
        
    def sendRaw(self, data, type=M_NONE):
        if type == M_TCP:
            socket = self.socket_tcp
            socketname = "TCP" # for errors
        elif type == M_UDP:
            socket = self.socket_udp
            socketname = "UDP" # for errors
        else:
            LOG.error("cannot send: unknown type")
            return False
        if socket is None:
            # not connected
            LOG.error("cannot send: " + socketname + " not connected!")
            return False
        try:
            # send the data
            socket.send(data)
        except socket.error, e:
            LOG.error("send error: %d (%s)" % (e[0], e[1]))
        return True
            

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
        payload = struct.pack(format_payload, serverversion, playername, playas, netlang, uniqueid)
        
        self.sendMsg_TCP(PACKET_CLIENT_JOIN, payload)

        
    def sendMsg(self, type, command, payload = ""):
        header = struct.pack(self.header_format, self.header_size + len(payload), command)
        return self.sendRaw(header + payload, type)
    def sendMsg_TCP(self, *args, **kwargs):
        return self.sendMsg(M_TCP, *args, **kwargs)
    def sendMsg_UDP(self, *args, **kwargs):
        return self.sendMsg(M_UDP, *args, **kwargs)
    def receiveMsg_UDP(self):
        try:
            if self.socket_udp is None:
                return None
            data = self.socket_udp.recv(4096)
            #print data
            [size, command], osize = unpackFromExt(self.header_format, data, 0)
            LOG.debug("received size: %d/%d, command: %d"% (size, osize, command))
            content = data[self.header_size:]
            
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
        #print "headersize: ", headersize
        data = ""
        readcounter = 0
        #LOG.debug( "receiving...")
        while len(data) < self.header_size:
            data += self.socket_tcp.recv(self.header_size-len(data))
            readcounter += 1
        if readcounter > 1:
            note += "HEADER SEGMENTED INTO %s SEGMENTS!" % readcounter
        
        (size, command) = struct.unpack(self.header_format, data)
        if not command in [PACKET_SERVER_FRAME, PACKET_SERVER_SYNC]:
            if command in packet_names.keys():
                LOG.debug("received size: %d, command: %s (%d)"% (size, packet_names[command], command))
            else:
                LOG.debug("received size: %d, command: %d"% (size, command))
        size -= self.header_size # remove size of the header ...
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
        if len(note) > 0:
            LOG.info(note)
        
        return size, command, data
        #content = struct.unpack(str(size) + 's', data)
        #content = content[0]

        #LOG.debug(size, command, content)
    def dateToYMD(self, date):
        ymddate = datetime.date.fromordinal(date - 365)
        return (ymddate.year, ymddate.month, ymddate.day)

        
