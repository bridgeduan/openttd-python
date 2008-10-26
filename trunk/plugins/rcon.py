# Plugin for openttd-python
# made by yorick (yorickvanpelt {AT} gmail {DOT} com)
import pluginclass
import openttd.structz
import openttd.constants as const

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
        payload = openttd.structz.pack('zz', argv[1], msg)
        self.client.sendMsg_TCP(const.PACKET_CLIENT_RCON, payload)
    def onPacket(self, command, content):
        if command == const.PACKET_SERVER_RCON and not self.lastevent is None:
            size, (color, message) = openttd.structz.unpack('Hz', content)
            self.lastevent.respond(message)
        