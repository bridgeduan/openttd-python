#!/bin/env python
# made by yorick
import client
import constants as const
from packet import DataPacket
from log import LOG
import socket
from datastorageclass import DataStorageClass
import structz

class ContentClient(client.Client):
    def __init__(self):
        client.Client.__init__(self, const.NETWORK_CONTENT_SERVER_HOST, const.NETWORK_CONTENT_SERVER_PORT)
    def connect(self):
        client.Client.connect(self, client.M_TCP)
    def disconnect(self):
        client.Client.disconnect(self, client.M_TCP)
    def ContentList_Request(self, type):
        if type == const.ContentType['END']:
            for t in const.ContentType:
                if t == 'BEGIN' or t == 'END': continue
                self.ContentList_Request(const.ContentType[t])
            return
        p = DataPacket(0, const.PACKET_CONTENT_CLIENT_INFO_LIST)
        p.send_uint8(type)
        p.send_uint32(0 << 28 | 8 << 24 | 0 << 20 | 0 << 19 | 0)
        self.sendMsg_TCP(p.command, p.data)
    def ContentList_Request_ids(self, ids):
        count = len(ids)
        sent = 0
        while count > 0:
            p_count = min((const.SEND_MTU - const.HEADER_SIZE - 4) / 4, count)
            p = DataPacket(0, const.PACKET_CONTENT_CLIENT_INFO_ID)
            p.send_uint16(p_count)
            for i in range(sent, p_count + sent):
                p.send_uint32(ids[i])
            self.sendMsg_TCP(p.command, p.data)
            count -= p_count
            sent += p_count
        
    def ContentList_Receive(self):
        self.socket_tcp.settimeout(1)
        while 1:
            try:
                p = self.receiveMsg_TCP(True)
            except socket.timeout:
                break
            self.ContentList_Process(p=p)
        self.socket_tcp.settimeout(600)
        
    def ContentList_Process(self, data="", p=None):
        structz.decodeerror = 'ignore'
        ci = DataStorageClass()
        ci.type     = p.recv_uint8()
        ci.id       = p.recv_uint32()
        ci.filesize = p.recv_uint32()
        
        ci.name        = p.recv_str()
        ci.version     = p.recv_str()
        ci.url         = p.recv_str()
        ci.description = p.recv_str()
        
        ci.unique_id   = p.recv_uint32()
        ci.md5sum      = p.recv_something('16s')
        
        ci.dependency_count = p.recv_uint8()
        ci.dependencies = []
        for i in range(ci.dependency_count):
            ci.dependencies.append(p.recv_uint32())
        
        ci.tag_count = p.recv_uint8()
        ci.tags = []
        for i in range(ci.tag_count):
            ci.tags.append(p.recv_str())
        
        self.ContentList.append(ci)
        structz.decodeerror = 'strict'

    def ContentList_Get(self):
        self.ContentList = []
        self.ContentList_Request(const.ContentType['END'])
        self.ContentList_Receive()
    def ContentList_PrintEntry(self, entry):
        print '-' * 50
        print '#%d  --  %s v%s' % (entry.id, entry.name, entry.version)
        print "%dkb - %s" % (entry.filesize / 1024, entry.url)
        print "%d dependencies:" % entry.dependency_count
        for dep in entry.dependencies:
            print " " * 10 + "%d" % dep
        print "%d tags:" % entry.tag_count + ", ".join(entry.tags)
        print "md5sum:", entry.md5sum[0].encode('hex')
        print "-"
        print entry.description
        
if __name__ == '__main__':
    c = ContentClient()
    c.connect()
    c.ContentList_Get()
    c.disconnect()
    for i in c.ContentList:
        c.ContentList_PrintEntry(i)
    
