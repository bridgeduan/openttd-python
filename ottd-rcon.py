#!/bin/env python
# made by yorickvanpelt {AT} gmail {DOT} com
# ottd_lib by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *
from struct_zerostrings import packExt, unpackExt, unpackFromExt

import ottd_constants as const

if platform.system() == 'Windows':
    # See http://msdn.microsoft.com/library/default.asp?url=/library/en-us/winprog/winprog/windows_api_reference.asp
    # for information on Windows APIs.
    STD_INPUT_HANDLE = -10
    STD_OUTPUT_HANDLE= -11
    STD_ERROR_HANDLE = -12

    FOREGROUND_BLUE = 0x01 # text color contains blue.
    FOREGROUND_GREEN= 0x02 # text color contains green.
    FOREGROUND_RED  = 0x04 # text color contains red.
    FOREGROUND_INTENSITY = 0x08 # text color is intensified.
    BACKGROUND_BLUE = 0x10 # background color contains blue.
    BACKGROUND_GREEN= 0x20 # background color contains green.
    BACKGROUND_RED  = 0x40 # background color contains red.
    BACKGROUND_INTENSITY = 0x80 # background color is intensified.

    import ctypes
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

def set_color(color, handle=std_out_handle):
    """(color) -> BOOL
    
    Example: set_color(FOREGROUND_GREEN | FOREGROUND_INTENSITY)
    """
    if platform.system() == 'Windows':
        return ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    else:
        colors = ['\x1b[34m', '\x1b[37m', '\x1b[33m', '\x1b[31m', '\x1b[35m', '\x1b[37m', '\x1b[33m', '\x1b[32m', '\x1b[37m', '\x1b[37m', '\x1b[35m', '\x1b[32m', '\x1b[37m', '\x1b[36m', '\x1b[30m\x1b[47m', '\x1b[35m', '\x1b[30m\x1b[47m']
        # todo: handle the linux case

    return False

def reset_color():
    if platform.system() == 'Windows':
        set_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)
    else:
        print '\x1b[49m\x1b[39m'
        # todo: handle the linux case

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
                if message == "":
                    runCond = False
                if color <= len(colors):
                    #setcolor(color)
                    print message
                    #reset_color()
                else:
                    print message
            else:
                if command == const.PACKET_SERVER_FULL:
                    print "ERROR: server full"
                elif command == const.PACKET_SERVER_BANNED:
                    print "ERROR: banned from server"
                elif command in const.packet_names:
                    print "ERROR: got unknown packet: %s" % const.packet_names[command]
                runCond = False
    if gotResponse:
        print "--  End of rcon response  --"
    client.disconnect()
    
if __name__ == '__main__':
    main()
