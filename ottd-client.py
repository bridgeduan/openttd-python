#!/bin/env python
import os
import os.path
import StringIO
import traceback
import time
from ottd_lib import LOG, M_TCP, M_UDP, M_BOTH, Client
from ottd_config import config, LoadConfig 
from struct_zerostrings import packExt, unpackExt, unpackFromExt
from ottd_client_event import IngameChat, IRCPublicChat, IRCPrivateChat, Broadcast, IngameToIRC, InternalCommand, IRCPublicActionChat, IRCToIngame

import ottd_constants as const

SVNREVISION = "$Rev$"

class SpectatorClient(Client):
    irc = None
    irc_server = config.get("irc", "server")
    irc_server_port = config.getint("irc", "serverport")
    irc_channel = config.get("irc", "channel")
    playerlist = {}
    webserver = None        
    
    # this class implements the thread start method
    def run(self):
        pass
    
    def sendChat(self, msg, desttype=const.DESTTYPE_BROADCAST, dest=0, chattype=const.NETWORK_ACTION_CHAT):
        payload = packExt('bbHz', chattype, desttype, dest, msg)
        payload_size = len(payload)
        self.sendMsg(const.PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
        
    def sendTCPmsg(self, msg, payload):
        self.sendMsg(msg, len(payload), payload, type=M_TCP)
        
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
        payload_size = len(payload)
        self.sendMsg(const.PACKET_CLIENT_COMMAND, payload_size, payload, type=M_TCP)
        
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


    def processCommand(self, event):
        LOG.debug("processing command '%s'" % event.msg)
        if not event.msg.startswith(config.get("main", "commandprefix")):
            return
        command = event.msg[1:]
        if config.has_option('irccommands', command):
            rawcommand = config.get('irccommands', command)
            if not len(rawcommand) > 0:
                return
                
            
            time_left=''
            time_running = ''
            if self.time_server_start >= 0 and self.time_server_runtime>=0:
                # get running time
                tl = time.time() - self.time_server_start
                if tl >= 86400:
                    time_running="%0.1f days"%(tl/86400.0)
                elif tl >= 3600:
                    time_running="%0.1f hours"%(tl/3600.0)
                elif tl >= 60:
                    time_running="%0.0f minutes"%(tl/60.0)
                else:
                    time_running="%0.0f seconds"%(tl)
                
                # get time left
                tl = self.time_server_runtime - (time.time() - self.time_server_start)
                if tl >= 86400:
                    time_left="%0.1f days"%(tl/86400.0)
                elif tl >= 3600:
                    time_left="%0.1f hours"%(tl/3600.0)
                elif tl >= 60:
                    time_left="%0.0f minutes"%(tl/60.0)
                else:
                    time_left="%0.0f seconds"%(tl)
                    
            botrevision = 'r'+SVNREVISION.strip('$').split(':')[-1].strip()
            interpolation = {
                "frame": self.frame_server,
                "time": time.ctime().__str__(),
                "ip": self.ip,
                "port": self.port,
                "ottdversion": self.revision,
                "botversion": botrevision,
                'time_left': time_left,
                'time_running': time_running,
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
                payload_size = len(payload)
                Broadcast("Reconnecting to server", parentclient=self, parent=event)
                self.sendMsg(const.PACKET_CLIENT_QUIT, payload_size, payload, type=M_TCP)

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
        payload_size = len(payload)
        self.reconnectCond = False
        self.sendMsg(const.PACKET_CLIENT_QUIT, payload_size, payload, type=M_TCP)
    
    def stopWebserver(self):
        if self.webserver:
            LOG.debug("stopping webserver ...")
            self.webserver.stop()
            self.webserver = None
            Broadcast("webserver stopped", parentclient=self)

    def on_irc_pubmsg(self, c, e):
        IRCPublicChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)

    def on_irc_privmsg(self, c, e):
        IRCPrivateChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)

    def on_irc_action(self, c, e):
        IRCPublicActionChat(e.arguments()[0], e.source().split('!')[0], parentclient=self, parentircevent=e)
    
    def on_irc_internal(self, msg):
        IRCToIngame(msg, parentclient=self)
        
    def handlePacket(self, command, content):
        if command == const.PACKET_SERVER_QUIT:
            [cid, msg], size = unpackExt('Hz', content)
            if cid == self.client_id:
                self.runCond = False
                LOG.info("Quit from server")
            else:
                if cid in self.playerlist:
                    IngameToIRC("%s has quit the game (%s)" % (self.playerlist[cid]['name'], msg), parentclient=self)
                    del self.playerlist[cid]
        
        elif command == const.PACKET_SERVER_ERROR:
            [errornum], size = unpackFromExt('B', content, 0)
            if errornum in const.error_names:
                IngameToIRC("Disconnected from server: %s" % const.error_names[errornum][1], parentclient=self)
            self.runCond = False
        
        elif command == const.PACKET_SERVER_ERROR_QUIT:
            [cid, errornum], size = unpackExt('HB', content)
            if cid == self.client_id:
                self.doingloop = False
                LOG.info("Disconnected from server")
            if cid in self.playerlist:
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
            self.playerlist[cid] = {'name':name, 'company':playas, 'lastactive':-1}
        
        elif command == const.PACKET_SERVER_JOIN:
            [playerid], size = unpackFromExt('H', content, 0)
            if playerid in self.playerlist and playerid != self.client_id:
                IngameToIRC("%s has joined the game" % self.playerlist[playerid]['name'], parentclient=self)
        
        if command == const.PACKET_SERVER_SHUTDOWN:
            Broadcast("Server shutting down...", parentclient=self)
            self.runCond = False
            self.reconnectCond = False
        
        if command == const.PACKET_SERVER_NEWGAME:
            Broadcast("Server loading new map...", parentclient=self)
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
        value = [self.getGameInfo(), self.getCompanyInfo()]
        
        tstart = time.time()
        fn = config.get("stats", "cachefilename")
        obj=[]
        try:
            f = open(fn, 'rb')
            obj = pickle.load(f)
            f.close()
        except IOError:
            LOG.error("error while opening stats cache file!")
            obj = []
        
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
    
    def joinGame(self):
        self.time_server_start=-1
        self.time_server_runtime=-1
        if config.getboolean('timewarning', 'enable'):
            timestr=''
            try:
                f=open(config.get('timewarning', 'starttimefile'), 'r')
                timestr = f.read()
                f.close()
            except:
                LOG.error("error while reading starttimefile")
            if timestr != '':
                self.time_server_start=int(timestr.strip())
            
            self.time_server_runtime=config.getint('timewarning', 'time_running')
            
    
        #construct join packet
        cversion = self.revision
        self.playername =  config.get("openttd", "nickname")
        password = 'citrus'
        self.playas = const.PLAYER_SPECTATOR
        language = const.NETLANG_ANY
        network_id =  config.get("openttd", "uniqueid")
        payload = packExt('zzBBz', cversion, self.playername, self.playas, language, network_id)
        payload_size = len(payload)
        #print "buffer size: %d" % payload_size
        self.sendMsg(const.PACKET_CLIENT_JOIN, payload_size, payload, type=M_TCP)
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
                self.sendMsg(const.PACKET_CLIENT_NEWGRFS_CHECKED, type=M_TCP)
                
            elif command == const.PACKET_SERVER_NEED_PASSWORD:
                [type,seed,uniqueid], size = unpackExt('BIz', content)
                if type == const.NETWORK_GAME_PASSWORD:
                    if self.password != '':
                        LOG.info("server is password protected, sending password ...")
                        payload = packExt('Bz', const.NETWORK_GAME_PASSWORD, self.password)
                        payload_size = len(payload)
                        self.sendMsg(const.PACKET_CLIENT_PASSWORD, payload_size, payload, type=M_TCP)
                    else:
                        LOG.info("server is password protected, but no pass provided, exiting!")
                        self.runCond=False
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
                self.sendMsg(const.PACKET_CLIENT_GETMAP, type=M_TCP)
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
                            LOG.info("starting downloading map!")
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
                
                self.sendMsg(const.PACKET_CLIENT_MAP_OK, type=M_TCP)
                
                # main loop, disable the timeout
                #self.socket_tcp.settimeout(600000000)
                frameCounter=73
                self.frame_server=0
                self.frame_max=0
                
                # init IRC bridge
                self.irc = None
                
                #self.processEvent(BotEvent("hey i am a bot :|"))
                
                # auto start IRC
                if config.getboolean("irc", "autojoin"):
                    self.startIRC()
                if config.getboolean("webserver", "autostart"):
                    self.startWebserver()
                
                ignoremsgs = []
                companyrefresh_interval = 120 #every two minutes
                companyrefresh_last = 0
                
                timewarning_interval = config.getint('timewarning', 'warning_interval')
                timewarning_last = 0
                
                doStats = config.getboolean("stats", "enable")
                if doStats:
                    self.clearStats()
                doTimeWarning = config.getboolean('timewarning', 'warnings')
                
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
                        
                    if frameCounter >= 74:
                        payload = packExt('I', self.frame_server)
                        payload_size = len(payload)
                        #print "sending ACK"
                        self.sendMsg(const.PACKET_CLIENT_ACK, payload_size, payload, type=M_TCP)
                        frameCounter=0
                    
                    if doStats and time.time() - companyrefresh_last > companyrefresh_interval:
                        self.updateStats()
                        companyrefresh_last = time.time()
                        
                    if doTimeWarning and time.time() - timewarning_last > timewarning_interval:
                        InternalCommand(config.get("main", "commandprefix") + "timeleft", self)
                        timewarning_last = time.time()
                    
                    if command == const.PACKET_SERVER_COMMAND:
                        [player, command2, p1, p2, tile, text, callback, frame, my_cmd], size = unpackFromExt('BIIIIzBIB', content)

                        commandid = command2 & 0xff
                        #print commandid
                        if commandid in const.command_names.keys():
                            LOG.debug("got command: %d(%s) from company %d: '%s'" % (commandid, const.command_names[commandid].__str__(), player, text))

                        #print player, command2, p1, p2, tile, text, callback, frame, my_cmd
    
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


def printUsage():
    import sys
    print "usage: %s <ip:port> <password>" % sys.argv[0]
    sys.exit(1)

def main():
    import sys
    # catch errors when we don't supply enough parameters  
    password = ''
    if len(sys.argv) == 0:
        printUsage()
    
    try:
        ip, port = sys.argv[1].split(':')
        port = int(port)
        if len(sys.argv) > 2:
            password = sys.argv[2]
    except Exception, e:
        #LOG.error(e)
        printUsage()

    client = SpectatorClient(ip, port, True)
    
    client.reconnectCond = True
    
    # endless loop
    while client.reconnectCond:
        # retry to connect every 20 seconds
        while not client.connect(M_BOTH):
            time.sleep(20)
        
        # sleep a second
        time.sleep(1)
        
        # fetch any fatal errors and try to reconnect to the server
        try:
            gameinfo = client.getGameInfo()
            client.revision = gameinfo.server_revision
            client.password = password
            client.joinGame()
            client.stopIRC()
            client.playerlist = {}
        except (KeyboardInterrupt, SystemExit):
            client.runCond = False
            client.reconnectCond = False
        except Exception, e:
            LOG.error('main loop error: '+str(e))
            errorMsg = StringIO.StringIO()
            traceback.print_exc(file=errorMsg)
            LOG.debug(errorMsg.getvalue())

    client.disconnect()
    sys.exit(0)

if __name__ == '__main__':
    main()
