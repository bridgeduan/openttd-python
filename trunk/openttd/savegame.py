#!/bin/env python
# reading openttd .sav files with python
# made by yorickvanpelt {AT} gmail {DOT} com
import structz
from constants import saveload_chunk_types
import array
import sys

class LoadException(Exception):
    """
    The exception raised by OTTDSaveGameParser when something goes wrong
    """
    pass

class CDataPacket:
    size=0
    data=0
    offset=0
    def __init__(self, data=""):
        self.size = len(data)
        self.data = data
        self.offset = 0
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
        return self.read_something('>B')[0]
    def read_int8(self):
        return self.read_something('>b')[0]
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
        return self.read_something('>H')[0]
    def read_int16(self):
        return self.read_something('>h')[0]
    def read_uint32(self):
        return self.read_something('>I')[0]
    def read_int32(self):
        return self.read_something('>i')[0]
    def read_uint64(self):
        return self.read_something('>Q')[0]
    def read_bool(self):
        return self.read_byte() != 0
    def write_str(self, string, leng=None):
        if not leng is None:
            return self.write_something(str(leng)+'s', [string])
        return self.write_something('z', [str])
    def write_uint8(self, i):
        return self.write_something('>B', [i])
    def write_uint16(self, i):
        return self.write_something('>H', [i])
    def write_uint32(self, i):
        return self.write_something('>I', [i])
    def write_uint64(self, i):
        return self.write_something('>Q', [i])
    def write_bool(self, b):
        if b:
            i = 1
        else:
            i = 0
        return self.write_something('B', [i])
    def read_OTTDSimpleGamma(self):
        HasBit = lambda x,y:(x & (1 << y)) != 0;
        i = self.read_byte()
        if HasBit(i, 7):
            i &= ~0x80
            if HasBit(i, 6):
                i &= ~0x40
                if HasBit(i, 5):
                    i &= ~0x20
                    if HasBit(i, 4):
                        raise LoadException("unsupported gamma")
                    i = (i << 8) | self.read_byte()
                i = (i <<  8) | self.read_byte()
            i = (i << 8) | self.read_byte()
        return i
    def read_array(self, format, number):
        a = array.array(format)
        end_offs = self.offset + structz.calcsize(format) * number
        a.fromstring(self.data[self.offset:end_offs])
        if sys.byteorder != 'big': a.byteswap()
        self.offset = end_offs
        return a.tolist()

class OTTDSaveGameParser:
    """
    openttd-python class to parse openttd savegames
    @ivar file: file used for reading/writing
    @type file: file
    @ivar mapsize: mapsize, ['known'] will be set to True when MAPS is handled, else, default of 256x256 is used
    @type mapsize: dict
    @ivar chunkhandlers: chunkhandlers looked for by findChunkHandler
    @type chunkhandlers: dict
    @ivar verbosity: verbosity (>1 will print chunk names when handling, >2 will print chunk names when loading too)
    @type verbosity: integer
    @ivar rdp: containing compressed savegame, just raw from/to the file
    @type rdp: CDataPacket instance
    @ivar save_format: savegame format used currently (OTTD, OTTZ, OTTN)
    @type save_format: string
    @ivar saveload_version: major savegame version
    @type saveload_version: integer
    @ivar saveload_minor_version: minor savegame version
    @type saveload_minor_version: integer
    @ivar data: compressed save data without header
    @type data: raw data string
    @ivar dp: containing uncompressed savegame data
    @type dp: CDataPacket instance
    @ivar chunks: all chunks loaded from file
    @type chunks: array
    """
    def __init__(self, filename="", file=None):
        """
        Constructor for OTTDSaveGameParser class
        @type filename:  string
        @param filename: filename to open if no file is specified
        @type file:      file
        @param file:     file to use, if not given, try to open file from filename
        """
        if file is None:
            self.file = open(filename, 'rb')
        else:
            self.file = file
        self.mapsize = {'x': 256, 'y': 256, 'known': False, 'total': 256*256}
        self.chunkHandlers = {}
        self.registerChunkHandlers()
        self.verbosity = 0
    def readfile(self):
        """
        Read the contents of the file open, close the file and destry its reference
        """
        rawdata = self.file.read()
        self.file.close()
        self.file = None
        self.rdp = CDataPacket(rawdata)
    def writefile(self, filename, file=None):
        """
        Write contents of the self.rdp to a file, and close the file afterwards
        @type  filename: string
        @param filename: filename to open if no file is specified
        @type  file:     file
        @param file:     file to use, if not given, try to open file from filename
        """
        if file is None:
            self.file = open(filename, 'wb')
        else:
            self.file = file
        self.file.write(self.rdp.data)
        self.file.close()
    def readsaveheader(self):
        """
        Read the savegame format, version and data and destroy self.rdp
        """
        self.save_format = self.rdp.read_str(4) # read the save format(compression format[LZO, ZLIB, NONE]
        slver = self.rdp.read_uint32()
        self.saveload_version = slver >> 16
        self.saveload_minor_version = (slver >> 8) & 0xFF # the minor savegame version is not used anymore from 18.0 on, but still there as it can't be removed easily
        self.data = self.rdp.data[self.rdp.offset:] # store the actual save data
        self.rdp = None # clean the rdp to save memory
    def writesaveheader(self, save_format, major_version, minor_version=0):
        """
        Create a savegame header with format, version and data into self.rdp
        @type  save_format:   string
        @param save_format:   save format to use (OTTZ, OTTN, OTTD)
        @type  major_version: int
        @type  minor_version: int
        @param major_version: major version to use
        @param minor_version: minor version to use ( 0 if not given)
        """
        self.rdp = CDataPacket()
        self.rdp.write_str(save_format, 4)
        self.rdp.write_uint32((major_version << 16) + (minor_version << 8)) # write the savegame version
        self.rdp.data += self.data
        self.rdp.size += len(self.data)
    def getSaveGameFormat(self, formatname=-1):
        """
        Get a savegame format defenition
        @type  formatname: string
        @param formatname: format to look for(uncompressed, LZO, ZLIB), if not given, this method returns the savegame format of the savegame currently loaded
        @rtype:   tuple
        @returns: tuple containing human readable description, the way it is stored in the savegame, function to uncompress, function to compress
        """
        def uncompressNone(data):
            return data
        def uncompressLZO(data):
            try:
                import lzo
            except ImportError:
                raise LoadException("can't load LZO saves, no LZO")
            else:
                return lzo.decompress(data)
        def uncompressZLIB(data):
            try:
                import zlib
            except ImportError:
                raise LoadException("can't load ZLIB saves, no ZLIB")
            else:
                return zlib.decompress(data)
        def compressNone(data):
            return data
        def compressLZO(data):
            try:
                import lzo
            except ImportError:
                raise LoadException("can't save LZO saves, no LZO")
            else:
                return lzo.compress(data)
        def compressZLIB(data):
            try:
                import zlib
            except ImportError:
                raise LoadException("can't save ZLIB saves, no ZLIB")
            else:
                return zlib.compress(data)                
        formats = (
            ("LZO"         , "OTTD", uncompressLZO , compressLZO ),
            ("uncompressed", "OTTN", uncompressNone, compressNone),
            ("ZLIB"        , "OTTZ", uncompressZLIB, compressZLIB),
        )
        if formatname == -1:
            for mat in formats:
                if mat[1] == self.save_format:
                    return mat
            else:
                raise LoadException("unknown save format")
        else:
            for mat in formats:
                if mat[0] == formatname:
                    return mat
            else:
                return -1
    def uncompress(self):
        """
        Looks up the savegameformat and uses its decompressor to decompress the data to to self.dp
        """
        decompressor = self.getSaveGameFormat()[2]
        self.dp = CDataPacket(decompressor(self.data))
    def compress(self, format="uncompressed"):
        """
        Looks up the savegameformat specified with the arguments and uses its compressor to compress the data to to self.data
        @type  format: string
        @param format: human readable format description to look for
        """
        compressor = self.getSaveGameFormat(format)[3]
        self.data = compressor(self.dp.data)
    def isSaveVersionBelow(self, major, minor=-1):
        """
        Checks if the savegame version is below a certain one
        @type  major: integer
        @type  minor: integer
        @param major: major savegame version to check for
        @param minor: minor savegame version, if not given, not checked at all
        @rtype:       boolean
        @returns:     True if the savegame version is below
        """
        if self.saveload_version < major:
            return True
        if minor != -1 and self.saveload_minor_version == major and self.saveload_minor_version < minor:
            return True
        return False
    def isSaveVersionEqualOrAbove(self, major, minor=-1):
        """
        Checks if the savegame version is equal or above a certain one
        @type  major: integer
        @type  minor: integer
        @param major: major savegame version to check for
        @param minor: minor savegame version, if not given, not checked at all
        @rtype:       boolean
        @returns:     True if the savegame version is above or equal
        """
        if self.saveload_version > major:
            return True
        if minor != -1 and self.saveload_major_version == major and self.saveload_minor_version >= minor:
            return True
        elif self.saveload_major_version == major:
            return True
        return False
    def findChunkHandler(self, chunkname, overwritehandlers={}):
        """
        Finds chunk handler in overwritehandlers and self.chunkHandlers, if False is specified instead of a function, a function that returns None is returned
        @type          chunkname: string
        @param         chunkname: chunkid to look for
        @type  overwritehandlers: dict
        @param overwritehandlers: checked before self.chunkHandlers
        @rtype:                   function
        @returns:                 chunk handler or a function that will return None
        """
        def nothing(*argv):
            return None
        if chunkname in overwritehandlers:
            if not overwritehandlers[chunkname] == False:
                return overwritehandlers[chunkname]
            else:
                return nothing
        elif chunkname in self.chunkHandlers:
            return self.chunkHandlers[chunkname]
        else:
            return nothing
    def registerChunkHandlers(self):
        """
        Will add all default chunkhandlers to the chunkhandlers array
        """
        c = self.chunkHandlers
        c['MAPS'] = self.readMAPS
        c['MAPT'] = self.readMAPT
        c['MAPO'] = self.readMAP1
        c['MAP2'] = self.readMAP2
        c['M3LO'] = self.readMAP3
        c['M3HI'] = self.readMAP4
        c['MAP5'] = self.readMAP5
        c['MAPE'] = self.readMAP6
        c['MAP7'] = self.readMAP7
        c['VIEW'] = self.readVIEW
        c['DATE'] = self.readDATE
        c['GLOG'] = self.readGLOG
        c['CHTS'] = self.readCHTS
    def loadChunks(self):
        """
        Load all chunks from the save and store them in self.chunks
        """
        chunks = []
        while True:
            curoffs = self.dp.offset
            id = self.dp.read_uint32()
            if id == 0:
                break
            name = "%c%c%c%c" % (id >> 24 & 0xFF, id >> 16 & 0xFF, id >> 8 & 0xFF, id & 0xFF)
            if self.verbosity > 2: print "loading chunk: %s"%name
            m = self.dp.read_byte()
            if m == saveload_chunk_types["CH_ARRAY"]: # array
                array = []
                index = 0
                while True:
                    leng    = self.dp.read_OTTDSimpleGamma()
                    curoffs = self.dp.offset
                    end_offset = curoffs + leng - 1  # todo: unsure if this is a correct approach ( the -1)
                    if leng == 0:
                        end_offset = self.dp.offset
                        break
                    array.append((index, self.dp.data[self.dp.offset:end_offset]))
                    index += 1
                    self.dp.offset = end_offset
                thischunk = ("CH_ARRAY", array)
            elif m == saveload_chunk_types["CH_SPARSE_ARRAY"]: # sparse array
                array = {}
                while True:
                    curoffs = self.dp.offset
                    leng    = self.dp.read_OTTDSimpleGamma()
                    if leng == 0:
                        end_offset = self.dp.offset
                        break
                    index = self.dp.read_OTTDSimpleGamma()
                    array[index] = self.dp.data[self.dp.offset:(curoffs+leng)]
                    self.dp.offset = curoffs + leng
                thischunk = ("CH_SPARSE_ARRAY", array)
            elif (m & 0xF) == saveload_chunk_types["CH_RIFF"]: # RIFF
                leng = ((self.dp.read_byte() << 16) | ((m >> 4) << 24)) + self.dp.read_uint16()
                end_offset = self.dp.offset + leng
                thischunk = ("CH_RIFF", self.dp.data[self.dp.offset:end_offset])
                self.dp.offset = end_offset
            else:
                raise LoadException("unknown chunk type")
            chunks.append((name, thischunk))
        self.chunks = chunks
    def handleChunks(self, chunkhandlers = {}):
        """
        Calls handleChunk for every entry in self.chunks
        """
        for chnk in self.chunks:
            self.handleChunk(chnk[0], chnk[1], chunkhandlers)
    def handleChunk(self, name, chunk, chunkoverrides = {}):
        """
        Call the chunkhandler for a specific chunk
        @type            name: string
        @type           chunk: raw data string
        @type  chunkoverrides: dict
        @param           name: name of the chunk
        @param          chunk: data to put in a CDataPacket instance and pass to the handler
        @param chunkoverrides: chunkoverrides to pass to findChunkHandler
        """
        chunktype = chunk[0]
        if self.verbosity > 1: print "parsing chunk: %s (%s)" % (name, chunktype)
        chunkhandler = self.findChunkHandler(name, chunkoverrides)
        if chunktype == "CH_ARRAY":
            for listitem in chunk[1]:
                dp = CDataPacket(listitem[1])
                chunkhandler(dp, dp.size, listitem[0])
        elif chunktype == "CH_SPARSE_ARRAY":
            for listkey in chunk[1]:
                dp = CDataPacket(chunk[1][listkey])
                chunkhandler(dp, dp.size, listkey)
        elif chunktype == "CH_RIFF":
            dp = CDataPacket(chunk[1])
            chunkhandler(dp, dp.size)
    # chunk handlers |/// -- start --
    def readMAPS(self, dp, chunksize):
        if self.saveload_version >= 6:
            self.mapsize['x'] = dp.read_uint32()
            self.mapsize['y'] = dp.read_uint32()
            self.mapsize['known'] = True
            self.mapsize['total'] = self.mapsize['x'] * self.mapsize['y']
    def readMAPT(self, dp, chunksize):
        type_height = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            type_height.extend(dp.read_array('B', 4096))
            i += 4096
        self.map_array = {}
        self.map_array['t'] = type_height
    def readMAP1(self, dp, chunksize):
        m1 = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            m1.extend(dp.read_bytes(4096))
            i += 4096
        self.map_array[1] = m1
    def readMAP2(self, dp, chunksize):
        m2 = []
        size = self.mapsize['total']
        if self.saveload_version > 5:
            i = 0
            while i < size:
                m2.extend(dp.read_array('H', 4096))
                i += 4096
        else:
            i = 0
            while i < size:
                m2.extend(dp.read_array('B', 4096))
                i += 4096
        self.map_array[2] = m2
    def readMAP3(self, dp, chunksize):
        m3 = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            m3.extend(dp.read_array('B', 4096))
            i += 4096
        self.map_array[3] = m3
                
    def readMAP4(self, dp, chunksize):
        m4 = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            m4.extend(dp.read_array('B', 4096))
            i += 4096
        self.map_array[4] = m4
                
    def readMAP5(self, dp, chunksize):
        m5 = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            m5.extend(dp.read_array('B', 4096))
            i += 4096
        self.map_array[5] = m5
    def readMAP6(self, dp, chunksize):
        GB = lambda x,s,n: (x >> s) & ((1 << n) - 1)
        m6 = []
        size = self.mapsize['total']
        if self.saveload_version <= 42:
            i = 0
            while i < size:
                j = 0
                while j != 1024:
                    buf = dp.read_byte()
                    m6.append(GB(buf, 0, 2))
                    m6.append(GB(buf, 2, 2))
                    m6.append(GB(buf, 4, 2))
                    m6.append(GB(buf, 6, 2))
                    i += 4
                    j += 1
        else:
            i = 0
            while i < size:
                m6.extend(dp.read_array('B', 4096))
                i += 4096
        self.map_array[6] = m6
    def readMAP7(self, dp, chunksize):
        m7 = []
        size = self.mapsize['total']
        i = 0
        while i < size:
            m7.extend(dp.read_array('B', 4096))
            i += 4096
        self.map_array[7] = m7
    def readVIEW(self, dp, chunksize):
        view = {}
        if self.saveload_version <= 5:
            view['x'] = dp.read_int16()
            view['y'] = dp.read_int16()
        else:
            view['x'] = dp.read_int32()
            view['y'] = dp.read_int32()
        view['z'] = dp.read_uint8()
        self.view = view
    def readDATE(self, dp, chunksize):
        date = {}
        if self.saveload_version <= 30:
            date['date'] = dp.read_uint16()
        else:
            date['date'] = dp.read_int32()
        date['date_fract'] = dp.read_uint16()
        date['tick_counter'] = dp.read_uint16()
        date['vehicle_id_ctr_day'] = dp.read_uint16()
        date['age_cargo_skip_counter'] = dp.read_uint8()
        if self.saveload_version <= 45:
            dp.read_something('x')
        if self.saveload_version <= 5:
            date['cur_tileloop_tile'] = dp.read_uint16()
        else:
            date['cur_tileloop_tile'] = dp.read_uint32()
        date['disaster_delay'] = dp.read_uint16()
        date['station_tick_ctr'] = dp.read_uint16()
        date['random_state1'] = dp.read_uint32()
        date['random_state2'] = dp.read_uint32()
        if self.saveload_version <= 9:
            date['cur_town_ctr'] = dp.read_uint8()
        else:
            date['cur_town_ctr'] = dp.read_uint32()
        date['cur_player_tick_index'] = dp.read_uint8()
        date['next_competitor_start'] = dp.read_uint16()
        date['trees_tick_ctr'] = dp.read_uint8()
        if self.saveload_version >= 4:
            date['pause_game'] = dp.read_uint8()
        if self.saveload_version >= 11:
            date['cur_town_iter'] = dp.read_uint32()
        self.date = date
    def readGLOG(self, dp, chunksize):
        logs = []
        at = 0
        while at != 0xFF:
            at = dp.read_byte()
            if at == 0xFF:
                break
            action = at
            tick = dp.read_uint16()
            
            ct = 0
            while ct != 0xFF:
                ct = dp.read_byte()
                if ct == 0xFF:
                    break
                if ct == 0: # mode
                    mode      = dp.read_uint8()
                    landscape = dp.read_uint8()
                    logs.append((tick, ct, (mode, landscape)))
                elif ct == 1: # revision
                    str      = dp.read_something('15s')[0].replace('\x00', "")
                    newgrf   = dp.read_uint32()
                    slver    = dp.read_uint16()
                    modified = dp.read_uint8()
                    logs.append((tick, ct, (str, newgrf, slver, modified)))
                elif ct == 2: # oldversion
                    type    = dp.read_uint32()
                    version = dp.read_uint32()
                    logs.append((tick, ct, (type, version)))
                elif ct == 3: # patch
                    name = dp.read_something('128s')[0].replace('\x00', '')
                    oldval = dp.read_uint32()
                    newval = dp.read_uint32()
                    logs.append((tick, ct, (name, oldval, newval)))
                elif ct == 4: # add grf
                    id  = dp.read_something('4s')[0].encode('hex')
                    md5 = dp.read_something('16s')[0].encode('hex')
                    logs.append((tick, ct, (id, md5)))
                elif ct == 5: # remove grf
                    id = dp.read_something('4s')[0].encode('hex')
                    logs.append((tick, ct, (id)))
                elif ct == 6: # grfcompat
                    id  = dp.read_something('4s')[0].encode('hex')
                    md5 = dp.read_something('16s')[0].encode('hex')
                    logs.append((tick, ct, (id, md5)))
                elif ct == 7: # param
                    id = dp.read_something('4s')[0].encode('hex')
                    logs.append((tick, ct, (id)))
                elif ct == 8: # move
                    id     = dp.read_something('4s')[0].encode('hex')
                    offset = dp.read_int32()
                    logs.append((tick, ct, (id, offset)))
                elif ct == 9: # bug
                    data = dp.read_uint64()
                    id   = dp.read_something('4s')[0].encode('hex')
                    bug  = dp.read_uint8()
                    logs.append((tick, ct, (data, id, bug)))
        self.gamelog = logs
    def readCHTS(self, dp, chunksize):
        cheats = []
        count = chunksize / 2
        for i in range(0, count):
            been_used = dp.read_bool()
            value     = dp.read_bool()
            cheats.append((been_used, value))
    # chunk handlers ///| -- end --
def parseArgs():
    import optparse
    # parse the arguments
    usage = "usage: %prog [options]"
    description = """This script will will parse an openttd savegame (http://www.openttd.org)
                    For more information, see the homepage: http://openttd-python.googlecode.com/."""
    argparser = optparse.OptionParser(usage=usage, description=description)
    argparser.set_defaults(file="network_tmp.sav", verbose=0, outformat="uncompressed", readmaparray=True)
    argparser.add_option("-f", "--file", dest="file", help="try to read from file FILE, if not given, default(network_tmp.sav) is used", type="string")
    argparser.add_option("-v", "--verbose", dest="verbose", action="count", help="being verbose?")
    argparser.add_option("-d", "--recompress", dest="recompress", metavar="OUTFILE", type="string", help="recompress and save to OUTFILE, will uncompress if outformat is not given")
    argparser.add_option("-o", "--outformat", dest="outformat", type="string", help="recompress using OUTFORMAT(LZO, ZLIB, uncompressed)")
    argparser.add_option("--skip-maparray", dest="readmaparray", help="do not read the map array", action="store_false")
    
    try:
        (options, args) = argparser.parse_args()
    except optparse.OptionError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
        return
    except TypeError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
    if hasattr(options, "recompress"):
        recompress = options.recompress
    else:
        recompress = None
    
        
    return (options.file, options.verbose, recompress, options.outformat, options.readmaparray)

def main():
    file, verbosity, recompress, outformat, readmaparray = parseArgs()
    s = OTTDSaveGameParser(file)
    s.verbosity = verbosity
    print "reading file \"%s\"" % file
    s.readfile()
    if verbosity > 0: print s.rdp.size, "bytes long"
    s.readsaveheader()
    print "savegame version %d.%d" % (s.saveload_version, s.saveload_minor_version)
    print "compressed with", s.getSaveGameFormat()[0]
    s.uncompress()
    chunkhandlers = {}
    if not readmaparray:
        c = chunkhandlers
        c['MAPT'] = False
        c['MAPO'] = False
        c['MAP2'] = False
        c['M3LO'] = False
        c['M3HI'] = False
        c['MAP5'] = False
        c['MAPE'] = False
        c['MAP7'] = False
    s.loadChunks()
    s.handleChunks(chunkhandlers)
    print "map size: %(x)dx%(y)d" % s.mapsize
    
    if not recompress is None:
        print "recompressing file"
        format = s.getSaveGameFormat(outformat)
        if format == -1:
            print "no such format"
            return
        s.compress(format[0]) # yes, compress also uncompresses :-p
        print "writing save header"
        s.writesaveheader(format[1], s.saveload_version, s.saveload_minor_version)
        print "saving file"
        s.writefile(recompress)

if __name__ == '__main__':
#    import psyco
#    psyco.full()
#    print "using psyco..."
    main()
