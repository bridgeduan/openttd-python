"""unpacking/packing zero-terminated strings with python"""
import struct

class Struct(object):
    """
    Class that allows you to use python 2.5-style struct objects with 2.4
    """
    def __init__(self, format):
        try:
            self._st = struct.Struct(format)
        except:
            self._st = None
            self._format = format
    def getsize(self):
        if not self._st is None:
            return self._st.size
        else:
            return struct.calcsize(self._format)
    size = property(fget=getsize, doc="The calculated size of the struct (and hence of the string) corresponding to format.")
    def getformat(self):
        if not self._st is None:
            return self._st.format
        else:
            return self._format
    def setformat(self, format):
        if not self._st is None:
            self._st = struct.Struct(format)
        else:
            self._format = format
            self._st = None
    format = property(fget=getformat, fset=setformat, doc="The format string used to construct this object.")
    def unpack(self, str):
        if not self._st is None:
            return self._st.unpack(str)
        else:
            return struct.unpack(self._format, str)
    def unpack_from(self, str, offset=0):
        if not self._st is None:
            return self._st.unpack_from(str, offset)
        else:
            return self.unpack(str[offset:offset+self.getsize()])
    def pack(self, *argv):
        if not self._st is None:
            return self._st.pack(*argv)
        else:
            return struct.pack(self._format, *argv)
    def pack_into(self, buffer, offset, *argv):
        if not self._st is None:
            return self._st.pack_into(buffer, offset, *argv)
        else:
            return struct.pack_into(self._format, buffer, offset, *argv)

def getEfmt(fmt):
    """
    get the endianness format from a struct format
    @param fmt: struct format
    @type  fmt: string
    @rtype    : tuple
    @returns:   (endianness, struct format)
    """
    format = "<"
    if len(fmt) > 0 and fmt[0] in ('@','=','<','>','!'):
        format = fmt[0]
        if len(fmt) > 1:
            fmt = fmt[1:]
    return format, fmt
def get_zstring(str):
    """
    get the zero-string from a string
    @param str: read from
    @type  str: string
    @rtype:     tuple
    @returns:   size, string
    """
    pos = str.find("\x00")
    slice = str[:pos]
    size = len(slice) + 1
    return size, slice
def mak_zstring(str):
    """
    make a zero-string
    @param str: make from
    @type  str: string
    @rtype:     string
    @returns:   zero-terminated string
    """
    return str+"\x00"
    
def unpack(fmt, str):
    """
    unpacks a string
    @param fmt: format to use
    @type  fmt: string
    @param str: data to unpack
    @type  str: string
    @rtype:     tuple
    @returns:   unpacked data
    """
    e, fmt = getEfmt(fmt)
    if not "z" in fmt:
        # normal unpack
        s = Struct(e+fmt)
        return s.unpack(str)
    else:
        sl = fmt.split("z")
        offs = 0
        ind = 0
        string = str
        unp = []
        for f in sl:
            ind += 1
            if len(f) > 0:
                s = Struct(e+f)
                unp += list(s.unpack_from(string, offs))
                offs += s.size
            if not ind == len(sl):
                offplus, unpplus = get_zstring(string[offs:])
                offs += offplus
                unp.append(unpplus)
        if not offs is len(str):
            raise Exception("unpack requires string that matches format size, try to use unpack_from")
        return tuple(unp)
def pack(fmt, *argv):
    """
    packs a string
    @param fmt: format to use
    @type  fmt: string
    @param v1, v2...: data to pack
    @rtype:     string
    @returns:   packed data
    """
    e, fmt = getEfmt(fmt)
    if not "z" in fmt:
        # normal pack
        s = Struct(e+fmt)
        return s.size, s.pack(*argv)
    else:
        sl = fmt.split("z")
        ind = 0
        offs = 0
        p = ""
        for f in sl:
            ind += 1
            if len(f) > 0:
                # the normal part
                s = Struct(e+f)
                p += s.pack(*argv[offs:offs+len(f)])
                offs += len(f)
            if not ind == len(sl):
                # the zerostring
                p += mak_zstring(argv[offs])
                offs += 1
        return p
def unpack_from(fmt, str, offset=0):
    """
    same as unpack, but doesn't require same-length string as formatsize
    @param    fmt: format to use
    @type     fmt: string
    @param    str: data to unpack
    @type     str: string
    @param offset: unpack from here
    @type  offset: int
    @rtype:     tuple
    @returns:   (size, unpacked data)
    """
    e, fmt = getEfmt(fmt)
    if not "z" in fmt:
        # normal unpack
        s = Struct(e+fmt)
        return s.size, s.unpack_from(str, offset)
    else:
        sl = fmt.split("z")
        offs = 0
        ind = 0
        string = str[offset:]
        unp = []
        for f in sl:
            ind += 1
            if len(f) > 0:
                s = Struct(e+f)
                unp += list(s.unpack_from(string, offset))
                offs += s.size
            if not ind == len(sl):
                offplus, unpplus = get_zstring(string[offset:])
                offs += offplus
                unp.append(unpplus)
        return offs, tuple(unp)
    
def calc_size(fmt, *argv):
    """
    calculate the size of a format
    @param    fmt: format to use
    @type     fmt: string
    @param v1, v2...: data to pack
    @rtype:     int
    @returns:   size
    """
    if not "z" in fmt:
        # normal pack
        s = Struct(fmt)
        return s.size
    else:
        e, fmt = getEfmt(fmt)
        sl = fmt.split("z")
        ind = 0
        offs = 0
        p = ""
        size = 0
        for f in sl:
            ind += 1
            if len(f) > 0:
                # the normal part
                s = Struct(e+f)
                size += s.size
                offs += len(f)
            if not ind == len(sl):
                # the zerostring
                size += len(mak_zstring(argv[offs]))
                offs += 1
        return len(p)
