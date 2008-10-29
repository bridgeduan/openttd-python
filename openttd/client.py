#!/bin/env python
# made by thomas in 5 hours - no guarantees ;)
import sys, struct
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
from operator import itemgetter
import signal

from log import LOG
import structz
import constants as const
from datastorageclass import DataStorageClass
import _error
import networking

#connection modes
M_NONE = 0
M_TCP  = 1 << 0
M_UDP  = 1 << 1
M_BOTH = M_TCP | M_UDP

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
        size, ret = structz.unpack_from(type, self.data, self.offset)
        self.offset += size
        return ret
    def send_something(self, type, something):
        buf = structz.pack(type, *something)
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
    def __init__(self, ip="", port=0, debugLevel=0, uid=None):
        self.socket_udp = None
        self.socket_tcp = None
        self.errors     = []
        self.connectionmode = M_NONE
        self.ip         = ip
        self.port       = port
        self.debuglevel = debugLevel
        self.uid        = uid
        
        self.running    = True # sighandler will change this value
        self.lock       = threading.Lock()
        threading.Thread.__init__(self)
    def createsocket(self, mode=M_BOTH):
        if mode & M_TCP and self.socket_tcp is None:
            self.socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_tcp.settimeout(5)
        if mode & M_UDP and self.socket_udp is None:
            self.socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket_udp.settimeout(5)
        
    def connect(self, mode=M_BOTH):
        self.createsocket(mode)
        
        try:
            self.ip = socket.gethostbyname(self.ip)
        except Exception, e:
            raise _error.ConnectionError("problem resolving host %s: %s" % (str(self.ip), str(e)))
            
        LOG.debug("connecting to %s:%d" % (self.ip, self.port))
        
        if mode & M_TCP:
            self.socket_tcp.connect((self.ip, self.port))
        if mode & M_UDP:
            self.socket_udp.connect((self.ip, self.port))
        
        self.connectionmode |= mode
        self.running = True
        #self.getGameInfo()
        
        #self.throwRandomData()
        #self.packetTest()
        #self.sendMsg_UDP(const.PACKET_UDP_CLIENT_FIND_SERVER)
        #self.sendRaw(self.packetTest())
        #data=self.receiveMsg_UDP()
        
        LOG.debug( "connect finished" )
        return True
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

    def getServerList(self, addr=(const.NETWORK_MASTER_SERVER_HOST, const.NETWORK_MASTER_SERVER_PORT)):
        payload = struct.pack("B", const.NETWORK_MASTER_SERVER_VERSION)
        self.sendMsg_UDP(const.PACKET_UDP_CLIENT_GET_LIST, payload, addr=addr)
        p = self.receiveMsg_UDP(datapacket=True)
        if p.command == const.PACKET_UDP_MASTER_RESPONSE_LIST:
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
                raise _error.WrongVersion("master server list request", protocol_version, const.NETWORK_MASTER_SERVER_VERSION)

    
    def getGRFInfo(self, grfs, addr=None):
        p = DataPacket(0, const.PACKET_UDP_CLIENT_GET_NEWGRFS)
        p.send_uint8(len(grfs))
        for grf in grfs:
            p.send_something('4s16s', grf)
        self.sendMsg_UDP(p.command, p.data, addr=addr)
        p = self.receiveMsg_UDP(True, useaddr=not addr is None)
        if p is None:
            LOG.debug("unable to receive UDP packet")
            return None
        newgrfs = []
        if p.command == const.PACKET_UDP_SERVER_NEWGRFS:
            reply_count = p.recv_uint8()
            for i in range(0, reply_count):
                [grfid, md5sum] = p.recv_something('4s16s')
                grfname = p.recv_str()
                newgrfs.append([grfid, md5sum, grfname])

            LOG.debug("Got reply to grf request with %d grfs:" % reply_count)
            for grf in newgrfs:
                LOG.debug(" %s - %s - %s" % (grf[0].encode("hex"), grf[1].encode("hex"), grf[2]))
            
            if not addr is None:
                return p.addr, newgrfs
            else:
                return newgrfs
        else:
            raise _error.UnexpectedResponse("PACKET_UDP_CLIENT_GET_NEWGRFS", str(p.command))

    def getCompanyInfo(self):
        return self.CompanyInfo_Get()
    def CompanyInfo_Get(self, addr=None):
        self.CompanyInfo_Request(addr)
        return self.CompanyInfo_Get_Response(not addr is None)
    def CompanyInfo_Request(self, addr=None):
        """
        Requests the gameinfo from a certain address, or to the connected one
        @param addr: address to request from
        @type  addr: tuple with (ip, port)
        """
        if not addr is None:
            self.sendMsg_UDP(const.PACKET_UDP_CLIENT_DETAIL_INFO, addr=addr)
        else:
            self.sendMsg_UDP(const.PACKET_UDP_CLIENT_DETAIL_INFO)
    def CompanyInfo_Get_Response(self, useaddr=False):
        """
        Receives and processes a response
        @param     useaddr: to return the address or not
        @type      useaddr: bool
        @returns:           processed data or (addr, processed data)
        @rtype:             DataStorageClass or tuple
        """
        p = self.CompanyInfo_Receive(useaddr)
        info = self.CompanyInfo_Process(p=p)
        if useaddr:
            return p.addr, info
        else:
            return info
    def CompanyInfo_Receive(self, useaddr=False):
        """
        Receives the companyinfo (gives address if useaddr is True)
        @param useaddr: to return the address or not
        @type  useaddr: bool
        @returns:       received info
        @rtype:         DataPacket
        """
        p = self.receiveMsg_UDP(datapacket=True, useaddr=useaddr)
        if not p.command == const.PACKET_UDP_SERVER_DETAIL_INFO:
            raise _error.UnexpectedResponse("PACKET_UDP_CLIENT_DETAIL_INFO", str(p.command))
        return p
    def CompanyInfo_Process(self, data="", p=None):
        """
        Processes a companyinfo response
        @param           p: DataPacket to read from
        @type            p: DataPacket
        @param        data: data to use when p is not given
        @type         data: string
        @returns:           processed data
        @rtype:             DataStorageClass
        """
        if p is None:
            p = DataPacket(len(data), const.PACKET_UDP_SERVER_DETAIL_INFO, data)
        info_version = p.recv_uint8()
        player_count = p.recv_uint8()
        
        if info_version == const.NETWORK_COMPANY_INFO_VERSION or info_version == 4:
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
    def getTCPCompanyInfo(self):
        self.sendMsg_TCP(const.PACKET_CLIENT_COMPANY_INFO)
        p = self.receiveMsg_TCP(True)
        if res is None:
            return None
        if p.command == const.PACKET_SERVER_COMPANY_INFO:
            [info_version, player_count] = p.recv_something('BB')
            if info_version == const.NETWORK_COMPANY_INFO_VERSION or info_version == 4: #4 and 5 are the same:
                companies = []
                firsttime = True
                for i in range(0, player_count):
                    if not firsttime:
                        p = self.receiveMsg_TCP(True)
                        if p is None:
                            return None
                        if p.command != const.PACKET_SERVER_COMPANY_INFO:
                            raise _error.UnexpectedResponse("PACKET_CLIENT_COMPANY_INFO", str(p.command))
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
                raise _error.WrongVersion("PACKET_CLIENT_COMPANY_INFO", info_version, const.NETWORK_COMPANY_INFO_VERSION)
        else:
            raise _error.UnexpectedResponse("PACKET_CLIENT_COMPANY_INFO", str(command))
    
    def getGameInfo(self, encode_grfs=False, short=False, addr=None):
        return self.GameInfo_Get(addr, encode_grfs, short)
    def processGameInfoResponse(self, size, command, content, encode_grfs, short):
        return self.GameInfo_Process(content, encode_grfs=encode_grfs, short=short)
    def GameInfo_Get(self, addr=None, encode_grfs=False, short=False):
        self.GameInfo_Request(addr)
        return self.GameInfo_Get_Response(not addr is None, encode_grfs, short)
    def GameInfo_Request(self, addr=None):
        """
        Requests the gameinfo from a certain address, or to the connected one
        @param addr: address to request from
        @type  addr: tuple with (ip, port)
        """
        if not addr is None:
            self.sendMsg_UDP(const.PACKET_UDP_CLIENT_FIND_SERVER, addr=addr)
        else:
            self.sendMsg_UDP(const.PACKET_UDP_CLIENT_FIND_SERVER)
    def GameInfo_Get_Response(self, useaddr=False, encode_grfs=False, short=False):
        """
        Receives and processes a response
        @param     useaddr: to return the address or not
        @type      useaddr: bool
        @param encode_grfs: return the grfs in hex if True
        @type  encode_grfs: bool
        @param       short: only return the things that could change?
        @type        short: bool
        @returns:           processed data or (addr, processed data)
        @rtype:             DataStorageClass or tuple
        """
        p = self.GameInfo_Receive(useaddr)
        info = self.GameInfo_Process(p=p, encode_grfs=encode_grfs, short=short)
        if useaddr:
            return p.addr, info
        else:
            return info
    def GameInfo_Receive(self, useaddr=False):
        """
        Receives the gameinfo (gives address if useaddr is True)
        @param useaddr: to return the address or not
        @type  useaddr: bool
        @returns:       received info
        @rtype:         DataPacket
        """
        p = self.receiveMsg_UDP(datapacket=True, useaddr=useaddr)
        if not p.command == const.PACKET_UDP_SERVER_RESPONSE:
            raise _error.UnexpectedResponse("PACKET_UDP_CLIENT_FIND_SERVER", str(p.command))
        return p
    def GameInfo_Process(self, data="", p=None, encode_grfs=False, short=False):
        """
        Processes a gameinfo response
        @param           p: DataPacket to read from
        @type            p: DataPacket
        @param        data: data to use when p is not given
        @type         data: string
        @param encode_grfs: return the grfs in hex if True
        @type  encode_grfs: bool
        @param       short: only return the things that could change?
        @type        short: bool
        @returns:           processed data
        @rtype:             DataStorageClass
        """
        if p is None:
            p = DataPacket(len(data), const.PACKET_UDP_SERVER_RESPONSE, data)
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
                info.game_date  = p.recv_uint16() + const.DAYS_TILL_ORIGINAL_BASE_YEAR
                if not short:
                    info.start_date = p.recv_uint16() + const.DAYS_TILL_ORIGINAL_BASE_YEAR
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
        
        
        
    def sendRaw(self, data, type, addr=None):
        if type == M_TCP:
            s = self.socket_tcp
            socketname = "TCP" # for errors
            useaddr = False
        elif type == M_UDP:
            s = self.socket_udp
            socketname = "UDP" # for errors
            useaddr = True
        else:
            return
        if s is None:
            # not connected
            raise _error.ConnectionError("cannot send: " + socketname + " not connected!")
        if not addr is None and useaddr:
            s.sendto(data, 0, addr)
        else:
            # send the data
            s.send(data)
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
        
        self.sendMsg_TCP(const.PACKET_CLIENT_JOIN, payload)
    def sendMsg(self, type, command, payload = "", addr=None):
        header = networking.createPacketHeader(command, payload)
        return self.sendRaw(header + payload, type, addr)
    def sendMsg_TCP(self, *args, **kwargs):
        return self.sendMsg(M_TCP, *args, **kwargs)
    def sendMsg_UDP(self, *args, **kwargs):
        return self.sendMsg(M_UDP, *args, **kwargs)
    def receive_bytes(self, socket, bytes):
        data = ""
        readcounter = 0
        while len(data) < bytes and self.running:
            data += socket.recv(bytes - len(data))
            readcounter += 1
        return data, readcounter
    def receiveMsg_UDP(self, datapacket = False, useaddr = False):
        if self.socket_udp is None:
            raise _error.ConnectionError("no udp socket for receiving")
        if useaddr:
            data, addr = self.socket_udp.recvfrom(4096)
        else:
            data = self.socket_udp.recv(4096)
            addr = None
        #print data
        size, command = networking.parsePacketHeader(data)
        LOG.debug("received size: %d, command: %d"% (size, command))
        content = data[const.HEADER.size:]
        if datapacket:
            ret = DataPacket(size, command, content)
            ret.addr = addr
        else:
            if useaddr:
                ret = addr, size, command, content
            else:
                ret = size, command, content
        return ret

    def receiveMsg_TCP(self, datapacket = False):
        if self.socket_tcp is None:
            raise _error.ConnectionError("no tcp socket for receiving")
        raw = ""
        note = ""
        data, readcounter = self.receive_bytes(self.socket_tcp, const.HEADER.size)
        if readcounter > 1:
            note += "HEADER SEGMENTED INTO %s SEGMENTS!" % readcounter
        raw += data
        size, command = networking.parsePacketHeader(data)
        if not command in (const.PACKET_SERVER_FRAME, const.PACKET_SERVER_SYNC):
            if command in const.packet_names:
                LOG.debug("received size: %d, command: %s (%d)"% (size, const.packet_names[command], command))
            else:
                LOG.debug("received size: %d, command: %d"% (size, command))
        size -= const.HEADER.size # remove size of the header ...
        data, readcounter = self.receive_bytes(self.socket_tcp, size)
        if readcounter > 1:
            note += "DATA SEGMENTED INTO %s SEGMENTS!" % readcounter
        raw += data
        if not self.running:
            return None
        if len(note) > 0:
            LOG.info(note)
        content = data
        
        if datapacket:
            return DataPacket(size, command, content)
        else:
            return size, command, content
        #content = struct.unpack(str(size) + 's', data)
        #content = content[0]