# Plugin for openttd-python
# made by yorick (yorickvanpelt {AT} gmail {DOT} com)
import pluginclass
import struct_zerostrings
import ottd_constants as const

class RconPlugin(pluginclass.Plugin):
    lastevent = None
    def init(self):
        self.registerChatCommand("rcon", self.rconCommand)
        self.registerCallback("on_receive_packet", self.onPacket)
    def rconCommand(self, event, commandstr):
        argv = commandstr.split()
        if len(argv) < 3:
            event.respond("Usage: rcon <password> <msg>")
            return
        self.lastevent = event
        msg = commandstr[len(argv[0])+len(argv[1]) + 1:]
        payload = struct_zerostrings.packExt('zz', argv[1], msg)
        self.client.sendTCPmsg(const.PACKET_CLIENT_RCON, payload)
    def onPacket(self, command, content):
        if command == const.PACKET_SERVER_RCON and not self.lastevent is None:
            [color, message], size = struct_zerostrings.unpackExt('Hz', content)
            self.lastevent.respond(message)
        