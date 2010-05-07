#!/bin/env python
# made by yorick
import client
import constants as const
from packet import DataPacket
from log import LOG
import socket
from datastorageclass import DataStorageClass
import structz
import version
import httplib
import _error
class MirrorClient(httplib.HTTPConnection):
    def __init__(self):
        httplib.HTTPConnection.__init__(self, const.NETWORK_CONTENT_MIRROR_HOST, const.NETWORK_CONTENT_MIRROR_PORT)
    def connect(self):
        httplib.HTTPConnection.connect(self)
    def disconnect(self):
        httplib.HTTPConnection.close(self)
    def ContentList_URL_Get(self, ids):
        req = "\n".join([str(id) for id in ids]) + "\n"
        self.request("POST", const.NETWORK_CONTENT_MIRROR_URL, req, {'Content-Type': 'text/plain', 'Accept': 'text/plain', 'User-Agent':'OpenTTD-Python/0.0'})
        response = self.getresponse()
        if not response.status == httplib.OK:
            raise _error.HTTPError("Error getting url from mirror server: %s" % response.reason)
        data = response.read()
        print response.getheaders()
        return [url.strip() for url in data.split() if len(url.strip()) > 0]
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
        p.send_uint32(version.generate_newgrf_version(1,1,0,False,0)) # XXX find better way?
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
    def ContentList_Get(self, id=const.ContentType['END']):
        self.ContentList = []
        self.ContentList_Request(id)
        self.ContentList_Receive()
    def ContentList_PrintEntry(self, entry):
        print '-' * 50
        print '#%d  (%13s)--  %s v%s %d' % (entry.id, const.ContentTypeDescr[entry.type], entry.name, entry.version, entry.unique_id)
        print "%dkb - %s" % (entry.filesize / 1024, entry.url)
        print "%d dependencies:" % entry.dependency_count
        for dep in entry.dependencies:
            print " " * 10 + "%d" % dep
        print "%d tags:" % entry.tag_count + ", ".join(entry.tags)
        print "md5sum:", entry.md5sum[0].encode('hex')
        print "-"
        print entry.description
import sys
def usage():
    print "OpenTTD Content Server Basic Script"
    print "Usage: %s command [arguments]" % sys.argv[0]
    print "Commands:"
    print "    help -- prints help"
    print "    list [contenttype] -- prints a list of entries"
    print "    geturl id1 [id2] [id3] ... -- prints the url of an entry"
    print "    getinfo id1 [id2] [id3] ... -- prints info about entries"
if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit()
    command = sys.argv[1].strip()
    if command == 'help':
        usage()
        sys.exit()
    elif command == 'list':
        id = const.ContentType['END']
        if len(sys.argv) > 2:
            if sys.argv[2].strip() in const.ContentType:
                id = const.ContentType[sys.argv[2].strip()]
            else:
                id = int(sys.argv[2])
        c = ContentClient()
        c.connect()
        c.ContentList_Get(id)
        c.disconnect()
        print "%d files:" % len(c.ContentList)
        for i in c.ContentList:
            c.ContentList_PrintEntry(i)
    elif command == 'geturl':
        c = MirrorClient()
        print c.ContentList_URL_Get(ids)
        c.close()
    elif command == 'getinfo':
        if len(sys.argv) < 3:
            sys.exit()
        ids = [int(i) for i in sys.argv[2:]]
        c = ContentClient()
        c.connect()
        c.ContentList = []
        c.ContentList_Request_ids(ids)
        c.ContentList_Receive()
        c.disconnect()
        for i in c.ContentList:
            c.ContentList_PrintEntry(i)
