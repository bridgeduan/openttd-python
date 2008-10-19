#!/bin/env python
import sys
import os
import os.path
import StringIO
import traceback
import time
from log import LOG
from openttd.client import M_TCP, M_UDP, M_BOTH, Client
from ottd_config import config, LoadConfig 
from struct_zerostrings import packExt, unpackExt, unpackFromExt
from ottd_client_event import IngameChat, IRCPublicChat, IRCPrivateChat, IRCPrivateNoticeChat, Broadcast, IngameToIRC, InternalCommand, IRCPublicActionChat, IRCPrivateActionChat, IRCToIngame

import plugins
import openttd.constants as const

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

SVNREVISION = "$Rev$"

class SpectatorClient(Client):
    irc = None
    irc_server = config.get("irc", "server")
    irc_server_port = config.getint("irc", "serverport")
    irc_channel = config.get("irc", "channel")
    playerlist = {}
    webserver = None        
    version = 'r'+SVNREVISION.strip('$').split(':')[-1].strip()
    callbacks = {
        "on_map_done": [],
        "on_user_join": [],
        "on_user_disconnect": [],
        "on_user_quit": [],
        "on_self_join": [],
        "on_self_quit": [],
        "on_server_newmap": [],
        "on_server_shutdown": [],
        "on_irc_user_join": [],
        "on_irc_user_quit": [],
        "on_irc_user_part": [],
        "on_irc_joined": [],
        "on_irc_kicked": [],
        "on_receive_command": [],
        "on_receive_packet": [],
        "on_frame": [],
        "on_mainloop": []
    }
    commands = {}
    
    # this class implements the thread start method
    def run(self):
        pass
    
    def sendChat(self, msg, desttype=const.DESTTYPE_BROADCAST, dest=0, chattype=const.NETWORK_ACTION_CHAT):
        payload = packExt('bbHz', chattype, desttype, dest, msg)
        self.sendMsg_TCP(const.PACKET_CLIENT_CHAT, payload)
        
    def sendTCPmsg(self, msg, payload):
        self.sendMsg_TCP(msg, payload)
        
    def sendCommand(self, command):
        """
        //    uint8:  PlayerID (0..MAX_PLAYERS-1)
        //    uint32: CommandID (see command.h)
        //    uint32: P1 (free variables used in DoCommand)
        //    uint32: P2
        //    uint32: Tile
        //    string: text
        //    uint8:  CallBackID (see callback_table.c)
        """
        p1 = 0
        p2 = 0
        tile = 2000
        text = "test123"
        cbid = 0
        player = self.playas
        payload = packExt('bIIIIzB', player, command, p1, p2, tile, text, cbid)
        self.sendMsg_TCP(const.PACKET_CLIENT_COMMAND, payload)
        
    def getCompanyString(self, id, withplayers=True):
        if withplayers:
            players = []
            for clientid2 in self.playerlist.keys():
                if self.playerlist[clientid2]['company'] == id:
                    players.append(self.playerlist[clientid2]['name'])
        if id == const.PLAYER_SPECTATOR:
            companystring = "spectators"
        else:
            companystring = "company %d" % (id+1)
        if withplayers:
            if len(players) < 4:
                return "%s (%s)" % (companystring, (", ".join(players)))
            else:
                return "%s (%d players)" % (companystring, len(players))
        else:
            return companystring
            
    def doCallback(self, callback, arguments=[]):
        if callback in self.callbacks:
            for callback in self.callbacks[callback]:
                callback(*arguments)


    def processCommand(self, event):
        LOG.debug("processing command '%s'" % event.msg)
        if not event.isCommand():
            return
        if not event.msg.startswith('!'):
            command = event.msg
        else:
            command = event.msg[1:]
        if config.has_option('irccommands', command):
            rawcommand = config.get('irccommands', command)
            if not len(rawcommand) > 0:
                return       
            interpolation = {
                "frame": self.frame_server,
                "time": time.ctime().__str__(),
                "ip": self.ip,
                "port": self.port,
                "ottdversion": self.revision,
                "botversion": self.version,
            }
            proccommand = rawcommand % interpolation
            if len(command) > 0:
                event.respond(proccommand)
        elif command == "activeplayers":
            #clients = []
            mytime = time.time()
            counter = 0
            for clientid in self.playerlist.keys():
                this_time = mytime - self.playerlist[clientid]['lastactive']
                if this_time < 60*5:
                    counter+=1
                    compstr = self.getCompanyString(self.playerlist[clientid]['company'])
                    timestr = "%d seconds ago" % (this_time)
                    event.respond("%s last active: %s"%(compstr, playerstr, timestr))
                #clients.append[this_time] = self.playerlist[clientid]
            if counter == 0:
                event.respond("no companies actively playing in the last 5 minutes")
        elif command == 'showplayers':
            for clientid in self.playerlist.keys():
                eventstr = "Client #%d: %s, playing in %s" % (clientid, self.playerlist[clientid]['name'], self.getCompanyString(self.playerlist[clientid]['company']))
                event.respond(eventstr)
        elif command.startswith('setupbridge') and not self.irc is None:
            arg = command[12:]
            if len(arg)<1:
                event.respond("Usage: !setupbridge <name>")
            else:
                if event.isFromIRC():
                    if arg in self.irc.bridges_ingame_irc:
                        event.respond("User already has a bridge")
                        return
                    if event.playername in self.irc.bridges_irc_ingame:
                        event.respond("You already have a bridge")
                    target = self.findPlayerByNick(arg)
                    if target is None:
                        event.respond("Unknown user (case sensitive!)")
                        return
                    self.irc.bridges_ingame_irc[arg] = event.playername
                    self.irc.bridges_irc_ingame[event.playername] = arg
                    event.respond("Set up bridge to %s" % arg)
                    self.sendChat("Set up a chatbridge from you to %s" % event.playername, desttype=const.DESTTYPE_CLIENT, dest=target['id'], chattype=const.NETWORK_ACTION_CHAT_CLIENT)
                else:
                    if arg in self.irc.bridges_irc_ingame:
                        event.respond("User already has a bridge")
                        return
                    if event.playername in self.irc.bridges_ingame_irc:
                        event.respond("You already have a bridge")
                    if not self.irc.bot.channels[self.irc.channel].has_user(arg):
                        event.respond("Unknown user (case sensitive!)")
                        return
                    self.irc.bridges_irc_ingame[arg] = event.playername.split('!')[0]
                    self.irc.bridges_ingame_irc[event.playername.split('!')[0]] = arg
                    self.irc.say_nick(arg, "Set up a chatbridge from you to %s" % event.playername, 0)
                    event.respond("Set up bridge to %s" % arg)
        elif command.startswith('removebridge') and not self.irc is None:
            if event.isFromIRC():
                if event.playername in self.irc.bridges_irc_ingame:
                    otherend = self.findPlayerByNick(self.irc.bridges_irc_ingame[event.playername])
                    if not otherend is None:
                        self.sendChat("Removed chatbridge", desttype=const.DESTTYPE_CLIENT, dest=otherend['id'], chattype=const.NETWORK_ACTION_CHAT_CLIENT)
                    del self.irc.bridges_ingame_irc[self.irc.bridges_irc_ingame[event.playername]]
                    del self.irc.bridges_irc_ingame[event.playername]
                    event.respond("Removed bridge")
                else:
                    event.respond("You currently don't have any bridge to ingame")
            else:
                if event.playername in self.irc.bridges_ingame_irc:
                    if self.irc.bot.channels[self.irc.channel].has_user(self.irc.bridges_ingame_irc[event.playername]):
                        self.irc.say_nick(self.irc.bridges_ingame_irc[event.playername], "removed chatbridge", 0)
                    del self.irc.bridges_irc_ingame[self.irc.bridges_ingame_irc[event.playername]]
                    del self.irc.bridges_ingame_irc[event.playername]
                    event.respond("Removed bridge")
                else:
                    event.respond("You currently don't have any bridge to IRC")
        elif command.startswith('notice') and not self.irc is None:
            arg = command[7:]
            if len(arg)<1:
                event.respond("Usage: !notice <name> <msg>")
            else:
                try:
                    name = arg.split(' ')[0]
                    msg = arg[len(name) + 1:]
                except:
                    event.respond("Usage: !notice <name> <msg>")
                    return
                if event.isFromIRC():
                    client = self.findPlayerByNick(name) 
                    if not client is None:
                        self.sendChat("[notice] <%s> %s" % (event.playername, msg), desttype=const.DESTTYPE_CLIENT, dest=client['id'], chattype=const.NETWORK_ACTION_CHAT_CLIENT)
                    else:
                        event.respond("Unknown player (case sensitive!)")
                else:
                    if self.irc.bot.channels[self.irc.channel].has_user(name):
                        self.irc.notice(name, "[notice] <%s> %s" % (event.playername, msg))
                    else:
                        event.respond("Unknown user (case sensitive!)")
                
        
        # non-useful commands for productive servers,, but the bot may use them itself all the time
        if not config.getboolean("main", "productive") or event.isByOp():
            #remove useless commands
            if command == 'quit':
                self.quit()
            elif command == 'reloadconfig':
                LoadConfig()
                Broadcast("reloading config file", parentclient=self, parent=event)
            elif command == 'reloadevents':
                reload(ottd_client_event)
            elif command == 'loadirc' and self.irc is None and config.getboolean("irc", "enable"):
                self.startIRC()
            elif command == 'unloadirc' and not self.irc is None:
                self.stopIRC()
                Broadcast("unloaded IRC", parentclient=self)
            elif command == 'startwebserver':
                self.startWebserver()
            elif command == 'stopwebserver':
                self.stopWebserver()
            elif command == 'reconnect':
                payload = packExt('z', "%s (reconnecting)" % config.get("openttd", "quitmessage"))
                Broadcast("Reconnecting to server", parentclient=self, parent=event)
                self.sendMsg_TCP(const.PACKET_CLIENT_QUIT, payload)
            elif command.startswith("load_plugin ") and len(command) > 12:
                arg = command[12:]
                plugins.load_plugin(arg)
                plugins.initialize_plugins(parent=self, module=arg)

        # cases not using if/elif
        if command.startswith("lastactive") and len(command) >11:
            arg = command[11:]
            companyid=-1
            if len(arg)<3:
                companyid = int(arg)
            else:
                for clientid in self.playerlist.keys():
                    if self.playerlist[clientid]['name'].lower().strip() == arg.lower().strip():
                        companyid=self.playerlist[clientid]['company']
            if companyid == -1:
                event.respond("company unknown")
            else:
                ltime = 0
                for clientid in self.playerlist.keys():
                    if self.playerlist[clientid]['company'] == companyid and self.playerlist[clientid]['lastactive'] > ltime:
                        ltime = self.playerlist[clientid]['lastactive']
                if ltime <=0:
                    timestr = " unkown"
                else:
                    timestr = "%d seconds ago" % (time.time()-ltime)
                event.respond("company %d last active: %s" % (companyid, timestr))
        commandstring = command.split()[0]
        if commandstring in self.commands:
            self.commands[commandstring](event, command)
        
    def startWebserver(self):
        if not config.getboolean("webserver", "enable") or not self.webserver is None:
            return
        from webserver import myWebServer
        LOG.debug("starting webserver ...")
        port = config.getint("webserver", "port")
        self.webserver = myWebServer(self, port)
        self.webserver.start()
        Broadcast("webserver started on port %d"%port, parentclient=self)
        
    def startIRC(self):
        from irc_lib import IRCBotThread
        self.irc = IRCBotThread(self.irc_channel, config.get("irc", "nickname"), self.irc_server, self, self.irc_server_port)
        self.irc.start()
        Broadcast("loading IRC", parentclient=self)

    def stopIRC(self):
        if not self.irc is None:
            try:
                self.irc.stop()
            except SystemExit:
                pass
            self.irc = None
    
    def quit(self):
        payload = packExt('z', config.get("openttd", "quitmessage"))
        self.reconnectCond = False
        self.sendMsg_TCP(const.PACKET_CLIENT_QUIT, payload)
    
    def stopWebserver(self):
        if self.webserver:
            LOG.debug("stopping webserver ...")
            self.webserver.stop()
            self.webserver = None
            Broadcast("webserver stopped", parentclient=self)

    def on_irc_pubmsg(self, c, e):
        if not e.source() is None and e.source().find('!') != -1:
            IRCPublicChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)

    def on_irc_privmsg(self, c, e):
        if not e.source() is None and e.source().find('!') != -1:
            IRCPrivateChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)
    
    def on_irc_notice(self, c, e):
        if not e.source() is None and e.source().find('!') != -1:
            IRCPrivateNoticeChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)

    def on_irc_action(self, c, e):
        if e.target() == self.irc.channel and not irc.source() is None and e.source().find('!') != -1:
            IRCPublicActionChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)
        elif not e.source() is None:
            # it is a private action
            IRCPrivateActionChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)
    
    def on_irc_internal(self, msg):
        IRCToIngame(msg, parentclient=self)
        
    def handlePacket(self, command, content):
        self.doCallback("on_receive_packet", [command, content])
        if command == const.PACKET_SERVER_QUIT:
            [cid, msg], size = unpackExt('Hz', content)
            if cid == self.client_id:
                self.runCond = False
                LOG.info("Quit from server")
                self.doCallback("on_self_quit", [-1, msg])
            else:
                if cid in self.playerlist:
                    IngameToIRC("%s has quit the game (%s)" % (self.playerlist[cid]['name'], msg), parentclient=self)
                    name = self.playerlist[cid]['name']
                    del self.playerlist[cid]
                    self.doCallback("on_user_quit", [name, msg])
                    if not self.irc is None and name in self.irc.bridges_ingame_irc:
                        # remove chatbridge
                        del self.irc.bridges_irc_ingame[self.irc.bridges_ingame_irc[name]]
                        del self.irc.bridges_ingame_irc[name]
        
        elif command == const.PACKET_SERVER_ERROR:
            [errornum], size = unpackFromExt('B', content, 0)
            self.doCallback("on_self_quit", [errornum])
            if errornum in const.error_names:
                IngameToIRC("Disconnected from server: %s" % const.error_names[errornum][1], parentclient=self)
            self.runCond = False
        
        elif command == const.PACKET_SERVER_ERROR_QUIT:
            [cid, errornum], size = unpackExt('HB', content)
            if cid == self.client_id:
                self.doingloop = False
                self.doCallback("on_self_quit", [errornum])
                LOG.info("Disconnected from server")
            if cid in self.playerlist:
                self.doCallback("on_user_disconnect", [self.playerlist[cid]['name'], errornum])
                IngameToIRC("%s has quit the game (%s)" % (self.playerlist[cid]['name'], const.error_names[errornum][1]), parentclient=self)
                del self.playerlist[cid]

        elif command == const.PACKET_SERVER_CLIENT_INFO:
            [cid, playas, name], size = unpackExt('HBz', content)
            if cid == self.client_id:
                self.playername = name
                self.playas = playas
            if cid in self.playerlist:
                if name != self.playerlist[cid]['name']:
                    IngameToIRC("%s changed nick to %s" % (self.playerlist[cid]['name'], name), parentclient=self)
                if playas != self.playerlist[cid]['company']:
                    IngameToIRC("%s has been moved to company %d" % (self.playerlist[cid]['name'], playas), parentclient=self)
            self.playerlist[cid] = {'name':name, 'company':playas, 'lastactive':-1, 'id': cid}
        
        elif command == const.PACKET_SERVER_JOIN:
            [playerid], size = unpackFromExt('H', content, 0)
            if playerid in self.playerlist:
                if playerid != self.client_id:
                    IngameToIRC("%s has joined the game" % self.playerlist[playerid]['name'], parentclient=self)
                    self.doCallback("on_user_join", [self.playerlist[playerid]])
                else:
                    self.doCallback("on_self_join")
        
        if command == const.PACKET_SERVER_SHUTDOWN:
            Broadcast("Server shutting down...", parentclient=self)
            self.doCallback("on_server_shutdown")
            self.runCond = False
            self.reconnectCond = False
        
        if command == const.PACKET_SERVER_NEWGAME:
            Broadcast("Server loading new map...", parentclient=self)
            self.doCallback("on_server_newmap")
            self.runCond = False
    
    def updateStats(self):
        available = True
        try:
            import pickle
        except ImportError:
            available=False
        if not available:
            LOG.error("error while loading pickle module, stats saving disabled!")
            return

        LOG.debug("updating stats...")
        tstart = time.time()
        
        fn = config.get("stats", "cachefilename")
        obj=[]
        firstSave=False
        try:
            f = open(fn, 'rb')
            obj = pickle.load(f)
            f.close()
        except IOError:
            firstSave=True
            
        value = [
                self.getGameInfo(encode_grfs=True, short=not firstSave),
                self.getCompanyInfo().companies,
                tstart
                ]
        
        obj.append(value)
        
        try:
            f = open(fn, 'wb')
            #if you use python < 2.3 use this line:
            #pickle.dump(obj, f)
            pickle.dump(obj, f, 1)
            f.close()
        except IOError:
            LOG.error("error while saving stats cache file!")
        
        tdiff = time.time() - tstart
        fs = float(os.path.getsize(fn)) / float(1024)
        LOG.debug("stats updated in %0.5f seconds. File is %.2fKB big (%d lines)"%(tdiff, fs, len(obj)))
    
    def clearStats(self):
        fn = config.get("stats", "cachefilename")
        try:
            os.remove(fn)
            LOG.debug("stats cleared")
        except:
            pass
    def findPlayerByNick(self, nick):
        for client in self.playerlist:
            if self.playerlist[client]['name'] == nick:
                return self.playerlist[client]
        return None
    
    def joinGame(self):
        #construct join packet
        cversion = self.revision
        self.playername =  config.get("openttd", "nickname")
        password = 'citrus'
        self.playas = const.PLAYER_SPECTATOR
        language = const.NETLANG_ANY
        network_id =  config.get("openttd", "uniqueid")
        payload = packExt('zzBBz', cversion, self.playername, self.playas, language, network_id)
        #print "buffer size: %d" % payload_size
        self.sendMsg_TCP(const.PACKET_CLIENT_JOIN, payload)
        self.runCond=True
        while self.runCond:
            size, command, content = self.receiveMsg_TCP()
            LOG.debug("got command %s" % const.packet_names[command])
            if command == const.PACKET_SERVER_FULL:
                LOG.info("Couldn't join server...it's full. Exiting!")
                self.runCond=False
            if command == const.PACKET_SERVER_BANNED:
                LOG.info("Couldn't join server...banned from it. Exiting!")
                self.runCond=False
                self.reconnectCond=False
            if command == const.PACKET_SERVER_CHECK_NEWGRFS:
                offset = 0
                [grfcount], size = unpackFromExt('B', content, offset)
                offset += size
                grfs = []
                if grfcount != 0:
                    for i in range(0, grfcount):
                        [grfid, md5sum], size = unpackFromExt('4s16s', content[offset:])
                        offset += size
                        grfs.append((grfid, md5sum))
                    LOG.debug("installed grfs (%d):" % len(grfs))
                    for grf in grfs:
                        LOG.debug(" %s - %s" % (grf[0].encode("hex"), grf[1].__str__().encode("hex")))
                LOG.debug("step2 - got installed GRFs, joining ...")
                self.sendMsg_TCP(const.PACKET_CLIENT_NEWGRFS_CHECKED)
                
            elif command == const.PACKET_SERVER_NEED_PASSWORD:
                [type,seed,uniqueid], size = unpackExt('BIz', content)
                if type == const.NETWORK_GAME_PASSWORD:
                    if self.password != '':
                        LOG.info("server is password protected, sending password ...")
                        payload = packExt('Bz', const.NETWORK_GAME_PASSWORD, self.password)
                        self.sendMsg_TCP(const.PACKET_CLIENT_PASSWORD, payload)
                    else:
                        LOG.info("server is password protected, but no pass provided, exiting!")
                        self.runCond=False
                        self.reconnectCond = False
                elif type == const.NETWORK_COMPANY_PASSWORD:
                    #if self.password != '':
                    #salted_password=""*32
                    #password="apassword"
                    #for i in range(1,32):
                    #    salted_password[i] = int(password[i]) ^ uniqueid[i] ^ (seed >> i)
                    #    LOG.info(i)
                    #LOG.info(salted_password)
                    #else:
                    LOG.info("company is password protected, not supported, exiting!")
                    self.runCond=False
                    self.reconnectCond=False

                
            elif command == const.PACKET_SERVER_WELCOME:
                LOG.info("yay, we are on the server :D (getting the map now ...)")
                
                [self.client_id, self.generation_seed, self.servernetworkid], size = unpackExt('HIz', content)
                
                self.socket_tcp.settimeout(600000000)
                
                downloadDone = False
                self.sendMsg_TCP(const.PACKET_CLIENT_GETMAP)
                mapsize_done = 0
                maptmp = None
                if config.getboolean("openttd", "savemap"):
                    maptmp = file(config.get("openttd", "savemapname"), 'wb')
                while not downloadDone and self.runCond:
                    size, command, content = self.receiveMsg_TCP()
                    
                    # first check if it is a command we need to run
                    self.handlePacket(command, content)
                    
                    if command == const.PACKET_SERVER_WAIT:
                        [num], res = unpackFromExt('B', content)
                        Broadcast("Waiting for map download...%d in line" % num, parentclient=self)
                    
                    if command == const.PACKET_SERVER_MAP:
                        offset = 0
                        [command2], size2 = unpackFromExt('B', content[offset:])
                        offset += size2
                        
                        if command2 == const.MAP_PACKET_START:
                            LOG.info("start downloading map!")
                            [framecounter], size2 = unpackFromExt('I', content[offset:])
                            offset += size2
                            
                            [position], size2 = unpackFromExt('I', content[offset:])
                            offset += size2
                        elif command2 == const.MAP_PACKET_NORMAL:
                            mapsize_done += size
                            if not maptmp is None:
                                maptmp.write(content[offset:])
                            if int(mapsize_done / 1024) % 100 == 0:
                                LOG.debug("got %d kB ..." % (mapsize_done / 1024))
                        elif command2 == const.MAP_PACKET_END:
                            LOG.info("done downloading map!")
                            if not maptmp is None:
                                maptmp.close()
                            downloadDone=True
                
                self.sendMsg_TCP(const.PACKET_CLIENT_MAP_OK)
                
                # main loop, disable the timeout
                #self.socket_tcp.settimeout(600000000)
                frameCounter=73
                self.frame_server=0
                self.frame_max=0
                
                #self.processEvent(BotEvent("hey i am a bot :|"))
                
                self.doCallback("on_map_done")
                
                # auto start IRC
                if config.getboolean("irc", "autojoin"):
                    self.startIRC()
                if config.getboolean("webserver", "autostart"):
                    self.startWebserver()
                
                ignoremsgs = []
                companyrefresh_interval = 120 #every two minutes
                companyrefresh_last = 0
                
                
                doStats = config.getboolean("stats", "enable")
                if doStats:
                    self.clearStats()
                
                while self.runCond:
                    size, command, content = self.receiveMsg_TCP()
                    #print content
                    self.handlePacket(command, content)
                    if command == const.PACKET_SERVER_FRAME:
                        old_framecounter = self.frame_server
                        [self.frame_server, self.frame_max], size = unpackFromExt('II', content)
                        #if self.debug:
                        #    print "got frame %d, %d" % (frame_server, frame_max)
                        frameCounter += (self.frame_server - old_framecounter)
                        self.doCallback("on_frame", [self.frame_server])
                        
                    if frameCounter >= 74:
                        payload = packExt('I', self.frame_server)
                        #print "sending ACK"
                        self.sendMsg_TCP(const.PACKET_CLIENT_ACK, payload)
                        frameCounter=0
                    
                    if doStats and time.time() - companyrefresh_last > companyrefresh_interval:
                        self.updateStats()
                        companyrefresh_last = time.time()
                    
                    if command == const.PACKET_SERVER_COMMAND:
                        [player, command2, p1, p2, tile, text, callback, frame, my_cmd], size = unpackFromExt('BIIIIzBIB', content)

                        commandid = command2 & 0xff
                        #print commandid
                        if commandid in const.command_names.keys():
                            LOG.debug("got command: %d(%s) from company %d: '%s'" % (commandid, const.command_names[commandid].__str__(), player, text))

                        #print player, command2, p1, p2, tile, text, callback, frame, my_cmd
                        self.doCallback("on_receive_command", [player, command2, p1, p2, tile, text, callback, frame, my_cmd])
    
                        """
                        # some example  implementation
                        companystr = self.getCompanyString(player)
                        if commandid == 61: #CMD_RENAME_SIGN
                            if text != '':
                                self.processEvent(BotEvent("%s renames a sign: '%s'" % (companystr, text)))
                        elif commandid == 46: #CMD_SET_PLAYER_COLOR
                            self.processEvent(BotEvent("%s changed their color"%companystr))
                        elif commandid == 52: #CMD_CHANGE_COMPANY_NAME
                            self.processEvent(BotEvent("%s changed their company name to '%s'"%(companystr, text)))
                        elif commandid == 53: #CMD_CHANGE_PRESIDENT_NAME
                            self.processEvent(BotEvent("%s changed their presidents name to '%s'"%(companystr, text)))
                        elif commandid == 43: #CMD_BUILD_INDUSTRY
                            self.processEvent(BotEvent("%s built a new industry"%(companystr)))
                        elif commandid == 44: #CMD_BUILD_COMPANY_HQ
                            self.processEvent(BotEvent("%s built their new HQ"%(companystr)))
                        """
    
                    if command == const.PACKET_SERVER_CHAT:
                        [actionid, playerid, self_sent, msg], size = unpackExt('bHbz', content)
                        self_sent = (playerid == self.client_id) or self_sent
                        if playerid in self.playerlist:
                            if not self_sent:
                                if actionid == const.NETWORK_ACTION_CHAT:
                                    IngameChat(msg, playerid, type="public", parentclient=self)
                                elif actionid == const.NETWORK_ACTION_CHAT_COMPANY:
                                    IngameChat(msg, playerid, type="team", parentclient=self)
                                elif actionid == const.NETWORK_ACTION_CHAT_CLIENT:
                                    IngameChat(msg, playerid, type="private", parentclient=self)
                        #LOG.debug(res.__str__())
                    self.doCallback("on_mainloop")
    def cleanup(self):
        self.disconnect()
        self.playerlist = {}


def parseArgs():
    import optparse
    # parse the arguments
    usage = "usage: %prog [ip[:port]] [options]"
    description = """This script will connect to an openttd server (http://www.openttd.org)
                    For more information, see the homepage: http://openttd-python.googlecode.com/."""
    argparser = optparse.OptionParser(usage=usage, description=description, version='r'+SVNREVISION.strip('$').split(':')[-1].strip())
    argparser.set_defaults(use_psyco=0)
    argparser.add_option("-p", "--password", dest="password", help="use password PASSWORD to join the server", type="string")
    argparser.add_option("--enable-psyco", dest="use_psyco", action="store_const", const=1, help="Force using psyco")
    argparser.add_option("--disable-psyco", dest="use_psyco", action="store_const", const=-1, help="Don't use psyco")
    
    try:
        (options, args) = argparser.parse_args()
    except optparse.OptionError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
        return
    except TypeError, err:
        print "Error while parsing arguments: ", err
        argparser.print_help()
    
    if len(args) == 0:
        ip = "127.0.0.1"
        port = 3979
    elif len(args) == 1:
        ipport = args[0].split(':')
        if len(ipport) == 1:
            ip = ipport[0]
            port = 3979
        elif len(ipport) == 2:
            ip = ipport[0]
            port = int(ipport[1])
    else:
        argparser.error("unknown argument count")
        
    if options.password:
        password = options.password
    else:
        password = ''
        
    return (ip, port, password, options.use_psyco, options)

def main():
    import sys
    ip, port, password, use_psyco, options = parseArgs()
        
    if use_psyco > -1:
        # Import Psyco if available
        try:
            import psyco
            psyco.full()
            print "using psyco..."
        except ImportError:
            if use_psyco > 0:
                print "Error: could not import psyco"
                sys.exit(1)

    client = SpectatorClient(ip, port, True)
    client.password = password
    client.reconnectCond = True
    client.cmdlineoptions = options

    plugins.load_plugins()
    plugins.initialize_plugins(client)
    
    
    # endless loop
    while client.reconnectCond:
        # retry to connect every 20 seconds
        while not client.connect(M_BOTH):
            time.sleep(20)
        
        # fetch any fatal errors and try to reconnect to the server
        try:
            gameinfo = client.getGameInfo()
            client.revision = gameinfo.server_revision
            client.joinGame()
            client.cleanup()
        except (KeyboardInterrupt, SystemExit):
            client.runCond = False
            client.reconnectCond = False
        except Exception, e:
            client.cleanup()
            LOG.error('main loop error: '+str(e))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            LOG.debug(errorMsg.getvalue())
            
        # sleep a second
        time.sleep(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
