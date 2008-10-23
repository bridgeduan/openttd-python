""" stuff that can be used for both client and server """
import struct
import constants as const

def hash_company_password(password, server_unique_id, game_seed):
    """
    hash a company password
    WARNING: this does not work and is still broken, its output is incorrect
    @param         password: password to hash
    @type          password: string
    @param server_unique_id: unique id of the server
    @type  server_unique_id: hex string
    @param        game_seed: game seed to use
    @type         game_seed: uint8
    @returns:                hashed password
    @rtype:                  hex string
    """
    if len(password) == 0:
        return ""
    uid_hash = server_unique_id.decode("hex")
    salted_pw = map(ord, password)
    salted_pw += [0] * (16-len(salted_pw)) # pad with zeros
    for i in range(0, 16):
        salted_pw[i] ^= ord(uid_hash[i]) ^ (game_seed >> i) & 0xFF
    sp = "".join(map(chr, salted_pw))
    try:
        import hashlib
        m = hashlib.md5()
    except ImportError:
        import md5
        m = md5.new()
    m.update(sp)
    hashed_pw = m.hexdigest()
    return hashed_pw

def createPacketHeader(command, payload):
    """
    create a packet header for payload PAYLOAD
    @param payload: payload to create header for
    @type  payload: string
    @param command: packet type
    @type  command: uint8
    """
    return const.HEADER.pack(const.HEADER.size + len(payload), command)
def parsePacketHeader(header):
    """
    parse a packet header
    @param header: header to read
    @type  header: string >= 3 long
    @rtype:        tuple
    @returns:      (size, packettype)
    """
    return const.HEADER.unpack_from(header)