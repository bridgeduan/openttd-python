# Plugin for openttd-python
# made by yorick (yorickvanpelt {AT} gmail {DOT} com)
import pluginclass
import openttd.structz
import openttd.constants as const
from ottd_config import config, WriteConfig


class RconPlugin(pluginclass.Plugin):
    lastevent = None
    def init(self):
        self.updateConfig()
        self.registerChatCommand("rcon", self.rconCommand)
        self.registerCallback("on_receive_packet", self.onPacket)
    def rconCommand(self, event, commandstr):
        if not config.getboolean("rcon", "enable"): return
        argv = commandstr.split()
        if event.isByOp() and len(config.get("rcon", "password")) > 0:
            msg = commandstr[len(argv[0]) + 1:]
            password = config.get("rcon", "password")
        elif len(argv) < 3:
            event.respond("Usage: rcon <password> <msg>")
            return
        else:
            msg = commandstr[len(argv[0]) + len(argv[1]) + 1:]
            password = argv[1]
        self.lastevent = event
        payload = openttd.structz.pack('zz', password, msg)
        self.client.sendMsg_TCP(const.PACKET_CLIENT_RCON, payload)
    def onPacket(self, command, content):
        if command == const.PACKET_SERVER_RCON and not self.lastevent is None:
            color, message = openttd.structz.unpack('Hz', content)
            self.lastevent.respond(message)
    def updateConfig(self):
        configchanged = False
        section_name = "rcon"
        if not config.has_section(section_name):
            config.add_section(section_name)
            configchanged = True
        options = {
            "enable":"Off",
            "password":""
        }
        for option in options: 
            if not config.has_option(section_name, option):
                config.set(section_name, option, options[option])
                configchanged = True
        if configchanged:
            WriteConfig()
        