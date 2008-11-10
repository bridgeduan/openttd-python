# ircbridges for openttd-python
# allows users to chat in private between irc and openttd
import pluginclass
import openttd.constants as const
from ottd_client_event import IngameChat, IRCChat

class Bridges(pluginclass.Plugin):
    def init(self):
        self.bridges_irc_ingame = {}
        self.bridges_ingame_irc = {}
        self.registerCallback("on_user_quit", self.ingame_quit)
        self.registerCallback("on_irc_user_quit", self.irc_quit)
        self.registerCallback("on_irc_user_part", self.irc_quit)
        self.registerChatCommand("setupbridge", self.setup_bridge)
        self.registerChatCommand("removebridge", self.remove_bridge)
        self.registerEventDispatcher(IngameChat, self.ingame_tobridge)
        self.registerEventDispatcher(IRCChat, self.irc_tobridge)
    def remove_bridge_irc_ingame(self, ircnick):
        if not ircnick in self.bridges_irc_ingame:
            return False
        ingamenick = self.bridges_irc_ingame[ircnick]
        if ingamenick in self.bridges_ingame_irc:
            del self.bridges_ingame_irc[ingamenick]
        del self.bridges_irc_ingame[ircnick]
        target = self.client.findPlayerByNick(ingamenick)
        if not target is None:
            self.client.sendChat("removed chatbridge to %s" % ircnick, desttype=const.DESTTYPE_CLIENT, dest=target['id'], chattype=const.NETWORK_ACTION_CHAT_CLIENT)
        return ingamenick
    def remove_bridge_ingame_irc(self, ingamenick):
        if not ingamenick in self.bridges_ingame_irc:
            return False
        ircnick = self.bridges_ingame_irc[ingamenick]
        if ircnick in self.bridges_irc_ingame:
            del self.bridges_irc_ingame[ircnick]
        del self.bridges_ingame_irc[ingamenick]
        if self.client.irc.bot.channels[self.client.irc.channel].has_user(ircnick.encode('latin-1')):
            self.client.irc.say_nick(ircnick, "removed chatbridge to %s" % ingamenick, 0)
        return ircnick
    def setup_bridge(self, event, command):
        if self.client.irc is None: return
        argv = command.split()
        if len(argv) != 2:
            event.respond("Usage: setupbridge <user>")
            return
        arg = argv[1]
        if event.isFromIRC():
            if event.playername in self.bridges_irc_ingame:
                event.respond("you already have a bridge")
                return
            if arg in self.bridges_ingame_irc:
                event.respond("%s already has a bridge" % arg)
                return
            target = self.client.findPlayerByNick(arg)
            if target is None:
                event.respond("Unknown user (case sensitive!)")
                return
            self.bridges_irc_ingame[event.playername] = arg
            self.bridges_ingame_irc[arg] = event.playername
            event.respond("Set up bridge to %s" % arg)
            self.client.sendChat("Set up a chatbridge from you to %s" % event.playername, desttype=const.DESTTYPE_CLIENT, dest=target['id'], chattype=const.NETWORK_ACTION_CHAT_CLIENT)
        else:
            if event.playername in self.bridges_ingame_irc:
                event.respond("You already have a bridge")
                return
            if arg in self.bridges_irc_ingame:
                event.respond("%s already has a bridge" % arg)
                return
            if not self.client.irc.bot.channels[self.client.irc.channel].has_user(arg.encode('latin-1')):
                event.respond("Unknown user (case sensitive!)")
                return
            self.bridges_ingame_irc[event.playername] = arg
            self.bridges_irc_ingame[arg] = event.playername
            self.client.irc.say_nick(arg, "Set up a chatbridge from you to %s" % event.playername, 0)
            event.respond("Set up bridge to %s" % arg)
    def remove_bridge(self, event, command):
        if self.client.irc is None: return
        if event.isFromIRC():
            if not event.playername in self.bridges_irc_ingame:
                event.respond("you don't have a bridge")
                return
            nick = self.remove_bridge_irc_ingame(event.playername)
            event.respond("removed bridge to %s" % nick)
        else:
            if not event.playername in self.bridges_ingame_irc:
                event.respond("you don't have a bridge")
                return
            nick = self.remove_bridge_ingame_irc(event.playername)
            event.respond("removed bridge to %s" % nick)
    def ingame_quit(self, name, msg):
        self.remove_bridge_ingame_irc(name)
    def irc_quit(self, c, e):
        nm_to_n = lambda nm: nm.split("!")[0]
        self.remove_bridge_irc_ingame(nm_to_n(e.source()))
    def ingame_tobridge(self, event):
        if event.type == "private" and not event.isCommand():
            if event.playername in self.bridges_ingame_irc:
                self.client.irc.say_nick(self.bridges_ingame_irc[event.playername], "[bridge] <%s> %s" % (event.playername, event.msg), 0)
    def irc_tobridge(self, event):
        if event.private and not event.notice and not event.isCommand():
            if event.playername in self.bridges_irc_ingame:
                target = self.client.findPlayerByNick(self.bridges_irc_ingame[event.playername])
                if target is None: return
                self.client.sendChat("[bridge] " + event.__str__(), const.DESTTYPE_CLIENT, target['id'], const.NETWORK_ACTION_CHAT_CLIENT)