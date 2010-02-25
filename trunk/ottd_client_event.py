#!/bin/env python
# event implementation for openttd-python bot script

from log import LOG
import openttd.constants as const
from ottd_config import config
import StringIO
import traceback

class Event:
    """
    Base event class
    @cvar dispatchTo: list of dispatchers
    @type dispatchTo: list
    """
    dispatchTo = ["sendToGame", "sendToIRC", "sendToLog", "sendToCmdProc"]
    def dispatch(self):
        """
        Dispatch an event to all dispatchers
        
        Calls every dispatcher in dispatchTo, if it's a string, it uses getattr, else, it tries to execute
        """
        for to in self.dispatchTo:
            if not type(to) == str:
                to(self)
            else:
                try:
                    function = getattr(self, to)
                except AttributeError:
                    LOG.error("Unknown dispatcher in %s: %s" % (self.__class__, to))
                else:
                    function()
    def sendToCmdProc(self):
        """
        The commandparser dispatcher
        @precondition: self.parentclient must not be None
        @rtype:  Boolean
        @return: False is the preconditions are not True
        """
        if self.parentclient is None:
            return False
        self.parentclient.processCommand(self)
        return True
class IngameChat(Event):
    """
    this event is generated by ingame chat
    @cvar   dispatchTo: list of dispatchers
    @type   dispatchTo: list
    @ivar         type: the type of this event (ingame, team, private)
    @type         type: string
    @ivar parentclient: the parent client
    @type parentclient: SpectatorClass instance
    @ivar       parent: the event that generated this event
    @type       parent: Event instance
    @ivar     playerid: the id of the client that generated this event
    @type     playerid: number
    @ivar playercompany: the company of the client that generated this event
    @type playercompany: number
    @ivar   playername: the name of the client that generated this event
    @type   playername: string
    @ivar          msg: the message
    @type          msg: string
    """
    dispatchTo = ["sendToIRC", "sendToLog", "sendToCmdProc"]
    def __init__(self, msg, clientid=-1, parent=None, parentclient=None, type=None):
        """
        Constructor for the IngameChat event
        @param          msg: the message
        @type           msg: string
        @param     clientid: the id of the client that generated this event
        @type      clientid: number
        @param       parent: the event that generated this event
        @type        parent: Event instance
        @param parentclient: the parent client
        @type  parentclient: SpectatorClass instnace
        @param         type: the type of this event (ingame, team, private)
        @type          type: string
        """
        self.type = type
        self.parentclient = parentclient
        self.parent = parent
        if not parent is None:
            # get stuff from parents
            try:
                if type is None and not self.parent.type is None:
                    self.type = self.parent.type
                if parentclient is None and not self.parent.parentclient is None:
                    self.parentclient = self.parent.parentclient
                if clientid == -1 and not self.parent.playerid == -1:
                    clientid = self.parent.playerid
                elif clientid == -1 and not self.parentclient is None:
                    clientid = self.parentclient.client_id
            except AttributeError:
                pass
        self.playerid = clientid
        self.msg = msg
        if clientid in self.parentclient.playerlist:
            self.playername = self.parentclient.playerlist[clientid]['name']
            self.playercompany = self.parentclient.playerlist[clientid]['company']
        self.dispatch()
    
    def isCommand(self):
        """
        Check if the message could be a command
        @rtype:  boolean
        @return: True if the msg could be a command(starts with the command prefix)
        """
        return self.msg.startswith(config.get("main", "commandprefix"))
    def respond(self, msg):
        """
        Respond to the event
        
        Initializes IngameChatResponse
        @param msg: message to respond with
        @type  msg: string
        """
        if not self.type is None:
            if self.type == "public" or self.type == "team":
                IngameChatResponse("%s: %s" % (self.playername, msg), self.playerid, self)
            elif self.type == "private":
                IngameChatResponse(msg, self.playerid, self)
    def sendToGame(self):
        """
        Dispatcher to game
        @precondition: self.type is not None
        @rtype: boolean
        @returns: True if the precondition is True
        """
        if not self.type is None:
            if self.type == "public":
                self.parentclient.sendChat(self.msg)
            elif self.type == "team":
                self.parentclient.sendChat(self.msg, desttype=const.DESTTYPE_TEAM, dest=self.playercompany, chattype=const.NETWORK_ACTION_CHAT_COMPANY)
            elif self.type == "private":
                self.parentclient.sendChat(self.msg, desttype=const.DESTTYPE_CLIENT, dest=self.playerid, chattype=const.NETWORK_ACTION_CHAT_CLIENT)
            return True
        return False
    def sendToLog(self):
        """
        Dispatcher to log
        @precondition: self.type is not None
        @rtype: boolean
        @returns: True if the precondition is True
        """
        if not self.type is None:
            if self.type == "public":
                LOG.info("Ingame chat: <%s> %s" % (self.playername,self.msg))
            elif self.type == "team":
                LOG.info("Ingame company chat: [%d]<%s> %s" % (self.playercompany, self.playername,self.msg))
            elif self.type == "private":
                LOG.info("Ingame private chat: <%s> %s" % (self.playername,self.msg))
            return True
        return False
    def sendToIRC(self):
        """
        Dispatcher to IRC
        @precondition: self.type is not None
        @precondition: self.parentclient.irc is not None
        @precondition: the event message is not a command
        """
        if self.parentclient.irc is None or self.isCommand() or self.type is None:
            return False
        if self.type == "public":
            self.parentclient.irc.say("<%s> %s" % (self.playername, self.msg), 0)   
        elif self.type == "team":
            self.parentclient.irc.say("[company: %d]<%s> %s" % (self.playercompany,self.playername, self.msg), 0)
        return True
    def isByOp(self):
        """
        Check if the command is from someone previledged, on IRC, this is an Op, ingame, this is the servr
        @rtype: boolean
        @returns: if the event is generated by the server
        """
        return self.playerid == 1
    def isFromIRC(self):
        """
        Check if the event comes from IRC
        @rtype: boolean
        @returns: False
        """
        return False


class IngameChatResponse(IngameChat):
    """
    The response to an IngameChatEvent
    @cvar dispatchTo: list of dispatchers
    @type dispatchTo: list
    """
    dispatchTo = ["sendToGame", "sendToLog"]
    def respond(self, msg):
        """
        Respond to the response, also known as do nothing
        @param msg: the message to respond with
        @type  msg: string
        """
        pass
    def sendToLog(self):
        """
        The event dispatcher to LOG
        @precondition: self.type is not None
        @rtype: boolean
        @returns: True if the preconditions are true
        """
        if self.type is None:
            return False
        if self.type == "public":
            LOG.info("Ingame public chat response: %s" % (self.msg))
        elif self.type == "team":
            LOG.info("Ingame team chat response: <To: %s> %s" % (self.playercompany, self.msg))
        elif self.type == "private":
            LOG.info("Ingame private chat response: <To: %s> %s" % (self.playername, self.msg))
        return True

class IRCChat(Event, object):
    """
        event generated by IRC chat
    """
    dispatchTo = ["sendToLog", "sendToCmdProc", "sendToGame"]
    def __init__(self, connection, event, parentclient=None, parent=None):
        self.connection = connection
        self.event = event
        if parentclient is None and not parent is None:
            self.parentclient = parent.parentclient
        else: self.parentclient = parentclient
        self.parent = parent
        self.dispatch()
    def _getMsg(self):
        return self.event.arguments()[0].decode('utf-8')
    def _getNick(self):
        if self.event.source() != None:
            result = self.event.source().split("!")[0]
        else:
            result = ""
        return result
    def _getChannel(self):
        trgt = self.event.target()
        is_channel = lambda c: c and c[0] in "#&+!"
        if is_channel(trgt): return trgt
        else: return None
    def _isPrivate(self):
        return self._getChannel() is None
    def _isAction(self):
        return self.event.eventtype() == "action"
    def _isNotice(self):
        return self.event.eventtype() == "privnotice" or self.event.eventtype() == "pubnotice"
    def _isPrivNotice(self):
        return self.event.eventtype() == "privnotice"
    msg = property(fget=_getMsg)
    playername = property(fget=_getNick)
    channel = property(fget=_getChannel)
    private = property(fget=_isPrivate)
    notice = property(fget=_isNotice)
    def isCommand(self):
        return self.msg.startswith(config.get("main", "commandprefix")) and not self._isAction()
    def sendToGame(self):
        if self.isCommand(): return False
        if not self.private:
            self.parentclient.sendChat(self.__str__())
            return True
    def sendToLog(self):
        if self.private:
            prefix = "IRC private chat: "
        else:
            prefix = "IRC chat: "
        LOG.info(prefix + self.__str__())
    def sendToCmdProc(self):
        if self.isCommand: return Event.sendToCmdProc(self)
    isFromIRC = lambda _: True
    def respond(self, msg):
        IRCChatResponse(msg, self.connection, self.event, self.parentclient, self)
    def isByOp(self):
        if self.private: return False
        return self.parentclient.irc.bot.channels[self.channel].is_oper(self.playername)
    def sendToIRC(self):
        if self.parentclient.irc is None or self.isCommand() or self.private: return False
        self.parentclient.irc.say(self.msg, 0)
    def __str__(self):
        if self._isAction():
            return "* %s %s" % (self.playername, self.msg)
        else:
            return "<%s> %s" % (self.playername, self.msg)
class IRCChatResponse(IRCChat):
    dispatchTo = ["sendToIRC", "sendToLog"]
    msg = None
    def __init__(self, msg, connection, parentircevent, parentclient=None, parent=None):
        self.msg = msg
        self.event = parentircevent
        self.connection = connection
        if parentclient is None and not parent is None:
            self.parentclient = parent.parentclient
        else: self.parentclient = parentclient
        self.parent = parent
        self.dispatch()
    def __str__(self):
        if self.private:
            return self.msg
        else:
            return "%s: %s" % (self.playername, self.msg)
    def sendToIRC(self):
        msg = self.__str__().encode('utf-8')
        if self.private:
            trgt = self.playername
        else:
            trgt = self.event.target()
        if not self._isAction() and not self._isNotice():
            self.connection.privmsg(trgt, msg)
        elif self._isNotice():
            self.connection.notice(trgt, msg)
        elif self._isAction():
            self.connection.action(trgt, msg)
    def sendToLog(self):
        if self.private:
            prefix = "IRC private chat response to %s: " % self.playername
        else:
            prefix = "IRC chat response: "
        LOG.info(prefix + self.__str__())
        
class Broadcast(IngameChat):
    """
    This event is generated by the bot itself when it needs to broadcast something
    @cvar dispatchTo: list of dispatchers
    @type dispatchTo: list
    """
    dispatchTo = ["sendToGame", "sendToIRC", "sendToLog"]
    def sendToGame(self):
        """
        Dispatcher to game
        @rtype: boolean
        @returns: True
        """
        self.parentclient.sendChat(self.msg)
        return True
    def sendToIRC(self):
        """
        Dispatcher to IRC
        @precondition: self.parentclient.irc is not None
        @rtype: boolean
        @returns: True if the precondition is True
        """
        if self.parentclient.irc is None:
            return False
        self.parentclient.irc.say(self.msg, 0)
        return True
    def sendToLog(self):
        """
        Dispatcher to LOG
        @rtype: boolean
        @returns: True
        """
        LOG.info("EVENT: %s" % (self.msg))
        return True

        
class IngameToIRC(Broadcast):
    """
        this event is generated by join/quit messages
    """
    dispatchTo = ["sendToIRC", "sendToLog"]
class IRCToIngame(Broadcast):
    """
        this event is generated by internal messages from irc"
    """
    dispatchTo = ["sendToGame", "sendToLog"]
class InternalCommand(Event):
    dispatchTo = ["sendToCmdProc"]
    def __init__(self, msg, parentclient=None):
        self.msg = msg
        self.parentclient = parentclient
        self.dispatch()
    def respond(self, msg):
        # this should not happen.
        Broadcast(msg, parentclient=self.parentclient, parent=self)
    def isByOp(self):
        return True
    def isCommand(self):
        return True
    def isFromIRC(self):
        return False
