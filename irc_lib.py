import socket, time, threading, copy
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr
from log import *
from ottd_config import *

class OTTDIRCBot(SingleServerIRCBot):
    runCond = True
    def __init__(self, channel, nickname, server, port=6667):
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel
        self.in_queue = []

    def process_forever(self, timeout=0.2):
        """Run an infinite loop, processing data from connections.

        This method repeatedly calls process_once.

        Arguments:

            timeout -- Parameter to pass to process_once.
        """
        while self.runCond:
            self.process_once(timeout)

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)
        self.in_queue.append(('', "IRC bridge running", 'internal'))

    def on_privmsg(self, c, e):
        self.in_queue.append((nm_to_n(e.source()), e.arguments()[0], e.eventtype()))

    def on_action(self, c, e):
        self.in_queue.append((nm_to_n(e.source()), e.arguments()[0], e.eventtype()))

    def on_pubmsg(self, c, e):
        self.in_queue.append((nm_to_n(e.source()), e.arguments()[0], e.eventtype()))
        
    def on_kick(self, c, e):
        self.in_queue.append(('', "we got kicked from the channel, trying to rejoin", 'internal'))
        c.join(self.channel)
    
    def say(self, msg, type):
        try:
            if type == 0:
                self.connection.privmsg(self.channel, msg)
            elif type == 1:
                self.connection.action(self.channel, msg)
        except:
            pass
        
    def getSaid(self):
        list = copy.copy(self.in_queue)
        self.in_queue = []
        return list
        
    def get_version(self):
        return "openttd-python client (http://openttd-python.googlecode.com)"

class IRCBotThread(threading.Thread):
    def __init__(self, channel, nickname, server, port=6667):
        self.channel=channel
        self.nickname=nickname
        self.server=server
        self.port=port
        self.bot=None
        threading.Thread.__init__(self)
        
    def run(self):
        self.bot = OTTDIRCBot(self.channel, self.nickname, self.server, self.port)
        self.bot.start()
        
    def stop(self, msg="Goodbye"):
        self.bot.runCond = False
        self.bot.disconnect(msg)
        
    def getSaid(self):
        if self.bot:
            return self.bot.getSaid()
        
    def say(self, msg, type):
        if self.bot:
            return self.bot.say(msg, type)