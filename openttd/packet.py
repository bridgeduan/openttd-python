import structz

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