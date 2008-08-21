#!/bin/env python
# made by yorickvanpelt {AT} gmail {DOT} com
# ottd_lib by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *
from struct_zerostrings import packExt, unpackExt, unpackFromExt

import ottd_constants as const


def printUsage():
	print "usage: %s <ip:port> \"password\" \"rcon\"" % sys.argv[0]
	sys.exit(1)
    
def main():
    if len(sys.argv) == 0:
		printUsage()
        
    try:
        ip, port = sys.argv[1].split(':')
        port = int(port)
        password = sys.argv[2]
        rcon = sys.argv[3]
    except:
        printUsage()
        return
    print "rconning to %s:%d with password %s:" % (ip, port, password)
    client = Client(ip, port)
    client.connect(M_TCP)
    payload = packExt('zz', password, rcon)
    payload_size = len(payload)
    client.sendMsg(const.PACKET_CLIENT_RCON, payload_size, payload, type=M_TCP)
    client.socket_tcp.settimeout(1)
    runCond = True
    gotResponse = False
    while runCond:
        try:
            size, command, content = client.receiveMsg_TCP()
        except:
            runCond = False
        else:
            if command == const.PACKET_SERVER_RCON:
                if not gotResponse:
                    print "-- Begin of rcon response --"
                gotResponse = True
                [color, message], size = unpackExt('Hz', content)
                print message
            else:
                runCond = False
    if gotResponse:
        print "-- End of rcon response --"
    client.disconnect()
    
if __name__ == '__main__':
    main()
