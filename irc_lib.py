import socket, time, threading, copy
from ircbot import SingleServerIRCBot, IRCDict
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr, IRC
from log import *
from ottd_config import *

class OTTDIRCBot(SingleServerIRCBot):
    runCond = True
    def __init__(self, channel, nickname, server, parentclient, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.ircobj.runCond = True
        self.channel = channel
        self.parentclient = parentclient

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.parentclient.on_irc_internal("IRC bridge running")
        self.parentclient.doCallback("on_irc_joined")

    def on_privmsg(self, c, e):
        self.parentclient.on_irc_privmsg(c, e)
    def on_privnotice(self, c, e):
        self.parentclient.on_irc_notice(c, e)

    def on_action(self, c, e):
        self.parentclient.on_irc_action(c, e)

    def on_pubmsg(self, c, e):
        self.parentclient.on_irc_pubmsg(c, e)
        
    def on_kick(self, c, e):
        self.parentclient.on_irc_internal("we got kicked from the channel, trying to rejoin")
        self.parentclient.doCallback("on_irc_kicked")
        c.join(self.channel)
    def on_join(self, c, e):
        self.parentclient.doCallback("on_irc_user_join", [c, e])
    def on_part(self, c, e):
        self.parentclient.doCallback("on_irc_user_part", [c, e])
    def on_quit(self, c, e):
        self.parentclient.doCallback("on_irc_user_quit", [c, e])
    
    def say(self, msg, type):
        try:
            if type == 0:
                self.connection.privmsg(self.channel, msg)
            elif type == 1:
                self.connection.action(self.channel, msg)
        except:
            pass
    
    def say_nick(self, nick, msg, type):
        try:
            if type == 0:
                self.connection.privmsg(nick, msg)
            elif type == 1:
                self.connection.action(nick, msg)
        except:
            pass
    def notice(self, nick, msg):
        try:
            self.connection.notice(nick, msg)
        except:
            pass
    def _on_disconnect(self, c, e):
        """[Internal]"""
        self.channels = IRCDict()
        if self.runCond:
            self.connection.execute_delayed(self.reconnection_interval,
                                            self._connected_checker)
        
    def get_version(self):
        return "openttd-python client %s (http://openttd-python.googlecode.com)" % self.parentclient.version


class IRCBotThread(threading.Thread):
    def __init__(self, channel, nickname, server, parentclient, port=6667):
        self.channel=channel
        self.nickname=nickname
        self.server=server
        self.port=port
        self.bot=None
        self.parentclient = parentclient
        self.bridges_irc_ingame = {}
        self.bridges_ingame_irc = {}
        threading.Thread.__init__(self)
        
    def run(self):
        self.bot = OTTDIRCBot(self.channel, self.nickname, self.server, self.parentclient, self.port)
        self.bot.start()
        
    def stop(self, msg="The ottdbot flies away!"):
        self.bot.runCond = False
        self.bot.ircobj.runCond = False
        self.bot.die(msg)
        
    def getSaid(self):
        if self.bot:
            return self.bot.getSaid()
        
    def say(self, msg, type):
        if self.bot:
            return self.bot.say(msg, type)
    def say_nick(self, nick, msg, type):
        try:
            if self.bot:
                return self.bot.say_nick(nick, msg, type)
        except:
            pass
    def notice(self, nick, msg):
        if self.bot:
            return self.bot.notice(nick, msg)
