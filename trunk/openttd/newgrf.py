#!/usr/bin/env python
# reading OpenTTD / TTDPatch GRF files with python
# made by yorickvanpelt {AT} gmail {DOT} com
import structz
import sys
class NewGRFDataPacket:
    size=0
    data=0
    offset=0
    def __init__(self, data=""):
        self.size = len(data)
        self.data = data
        self.offset = 0
    def read_raw(self, size):
        """
        This method gets raw data and returns it as string
        @param size: size of raw data to get
        @type  size: unsigned integer
        @rtype:      string/bytes
        @returns:    raw data
        """
        offs = self.offset
        self.offset += size
        return self.data[offs:self.offset]
    def read_something(self, type):
        """
        This method gets something from the data and returns it as array
        @param type: string containing types needed to unpack
        @type  type: string
        @rtype:      list
        @returns:    list with unpacked stuff
        """
        s = structz.Struct(type)
        ret = s.unpack_from(self.data, self.offset)
        self.offset += s.size
        return ret
    def write_something(self, type, something):
        """
        This method writes something to the data
        @param type:      string containing types needed to pack
        @type  type:      string
        @param something: list with stuff to be packed
        @type  something: list
        """
        s = structz.Struct(type)
        self.data += s.pack(*something)
        self.size += s.size
    def read_str(self, len):
        return self.read_something(str(len)+'s')[0]
    def read_uint8(self):
        return self.read_something('<B')[0]
    def read_int8(self):
        return self.read_something('<b')[0]
    def read_byte(self):
        """
        Reads a byte from the data using string operators
        @rtype:   int
        @returns: byte from the data
        """
        offs = self.offset
        self.offset += 1
        return ord(self.data[offs])
    def read_bytes(self, number):
        offs = self.offset
        self.offset += number
        data = map(ord, self.data[offs:self.offset])
        return tuple(data)
    def read_uint16(self):
        return self.read_something('<H')[0]
    def read_int16(self):
        return self.read_something('<h')[0]
    def read_uint32(self):
        return self.read_something('<I')[0]
    def read_int32(self):
        return self.read_something('<i')[0]
    def read_uint64(self):
        return self.read_something('<Q')[0]
    def read_bool(self):
        return self.read_byte() != 0
    def write_str(self, string, leng=None):
        if not leng is None:
            return self.write_something(str(leng)+'s', [string])
        return self.write_something('z', [str])
    def write_uint8(self, i):
        return self.write_something('<B', [i])
    def write_uint16(self, i):
        return self.write_something('<H', [i])
    def write_uint32(self, i):
        return self.write_something('<I', [i])
    def write_uint64(self, i):
        return self.write_something('<Q', [i])
    def write_bool(self, b):
        if b:
            i = 1
        else:
            i = 0
        return self.write_something('B', [i])
    def read_array(self, format, number):
        a = array.array(format)
        end_offs = self.offset + structz.calcsize(format) * number
        a.fromstring(self.data[self.offset:end_offs])
        if sys.byteorder != 'big': a.byteswap()
        self.offset = end_offs
        return a.tolist()
class NewGRFError(Exception):
    pass
class NewGRFDataError(NewGRFError):
    pass
class NewGRFCorruptSprite(NewGRFDataError):
    pass
class NewGRFSprite(object):
    """ Base class for newgrf sprites """
class NewGRFAction(NewGRFSprite):
    """ Class for newgrf action """
    def __init__(self, data):
        self.data = data
    def __str__(self):
        return "NewGRF Action(size %d): %s" % (self.size, self.data.encode('hex'))
    def get_size(self):
        return len(self.data)
    size = property(get_size)
class NewGRFFirstSprite(NewGRFSprite):
    """ Special length sprite """
    def __init__(self, data):
        self.data = data
        if not self.size == 4:
            raise NewGRFDataError("First sprite doesn't have length 4")
        self.content, = structz.unpack('<I', self.data)
    def __str__(self):
        return "NewGRF Length Sprite(size %d): %d" % (self.size, self.content)
    def get_size(self):
        return len(self.data) # should be 4
    size = property(get_size)
class NewGRFRealSprite(NewGRFSprite):
    def __init__(self):
        self.height = 0
        self.width  = 0
        self.x_offs = 0
        self.y_offs = 0
        self.type = 0
        self.data = ""
    def __str__(self):
        return "NewGRF Real Sprite"
class NewGRFPalette(object):
    def __init__(self, data=""):
        self.data = data
    def loadfrombcpfile(self, filename="", file=None):
        if file is None:
            self.file = open(filename, 'rb')
        else:
            self.file = file
        self.data = self.file.read()
        if file is None:
            self.file.close()
class NewGRFParser(object):
    def __init__(self, filename="", file=None):
        if file is None:
            self.file = open(filename, 'rb')
        else:
            self.file = file
        self.sprites = []
    def readfile(self):
        """
        Read the contents of the file open, close the file and destry its reference
        """
        rawdata = self.file.read()
        self.file.close()
        self.file = None
        self.rdp = NewGRFDataPacket(rawdata)
    def read_real_sprite(self, num, type):
        # algorithm "inspired" by OpenTTD src/spriteloader/grf.cpp
        sprite = NewGRFRealSprite()
        sprite.height = self.rdp.read_byte()
        sprite.width  = self.rdp.read_uint16()
        sprite.x_offs = self.rdp.read_int16()
        sprite.y_offs = self.rdp.read_int16()
        # 0x02 indicates it is a compressed sprite, so we can't rely on 'num' to be valid.
        # In case it is uncompressed, the size is 'num' - 8 (header-size).
        if type & 0x02:
            num = sprite.width * sprite.height
        else:
            num -= 8
        dest = ""
        dest_size = num
        # decompress
        while num > 0:
            code = self.rdp.read_int8()
            if code >= 0:
                # read plain bytes
                size = code
                if code == 0:
                    size = 0x80
                num -= size
                if num < 0:
                    raise NewGRFCorruptSprite()
                dest += self.rdp.read_raw(size)
            else:
                # copy bytes from earlier in the sprite
                data_offset = ((code & 7) << 8) | self.rdp.read_byte()
                if data_offset > len(dest):
                    raise NewGRFCorruptSprite()
                size = -(code >> 3)
                num -= size
                if num < 0:
                    raise NewGRFCorruptSprite()
                for i in range(size):
                    dest += dest[-data_offset]
        if type & 0x08: # When there are transparency pixels, this format has another trick.. decode it
            sprite.data = [chr(0)] * sprite.width * sprite.height
            for y in range(sprite.height):
                last_item = False
                # Look up in the header-table where the real data is stored for this row
                offset = (ord(dest[y*2+1]) << 8) | ord(dest[y * 2])
                while True:
                    if offset + 2 > len(dest):
                        raise NewGRFCorruptSprite()
                    last_item = ((ord(dest[offset])) & 0x80) != 0
                    length = ord(dest[offset]) & 0x7F
                    offset += 1
                    skip = ord(dest[offset])
                    offset += 1
                    if (skip + length > sprite.width) or (offset + length > len(dest)):
                        raise NewGRFCorruptSprite()
                    for x in range(length):
                        sprite.data[y * sprite.width + skip + x] = dest[offset]
                        offset += 1
                    if last_item: break
            sprite.data = ''.join(sprite.data)
        else:
            if len(dest) < sprite.width * sprite.height:
                raise NewGRFCorruptSprite()
            sprite.data = dest
        sprite.type = type
        self.sprites.append(sprite)
        return sprite
    def readsprite(self):
        size = self.rdp.read_uint16()
        if not size: return
        info = self.rdp.read_byte()
        if info == 0xFF:
            data = self.rdp.read_raw(size)
            spr = None
            if len(self.sprites) == 0:
                spr = NewGRFFirstSprite(data)
            else:
                spr = NewGRFAction(data)
            self.sprites.append(spr)
            return spr
        else:
            return self.read_real_sprite(size, info)
