#!/usr/bin/env python
import sys
import os
import os.path
import StringIO
import traceback
import time
from log import LOG
from openttd.client import M_TCP, M_UDP, M_BOTH, Client
from openttd.packet import DataPacket
from ottd_config import config, LoadConfig 
import openttd.networking
from openttd.datastorageclass import DataStorageClass
from openttd import structz, const
from ottd_client_event import IngameChat, Broadcast, IngameToIRC, InternalCommand, IRCToIngame
import openttd.version

import plugins
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))


SVNREVISION = "$Rev$"

class SpectatorClient(Client):
    irc = None
    irc_server = config.get("irc", "server")
    irc_server_port = config.getint("irc", "serverport")
    irc_channel = config.get("irc", "channel")
    version = 'r'+SVNREVISION.strip('$').split(':')[-1].strip()
    def __init__(self, ip, port, debugLevel, password, company=const.PLAYER_SPECTATOR, cpassword=""):
        Client.__init__(self, ip, port, debugLevel)
        self.password = password
        self.playas = company
        self.cpassword = cpassword
        self.reconnectCond = True
        self.playerlist = {}
        self.callbacks = {
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
        self.commands = {}

        self.plugins = {'modules': {}, 'instances': {}}
        plugins.load_plugins(self.plugins['modules'])
        plugins.initialize_plugins(self, obj=self.plugins['instances'])
    # this class implements the thread start method
    def run(self):
        # endless loop
        while self.reconnectCond:
            # retry to connect every 20 seconds
            while not self.connect(M_BOTH):
                time.sleep(20)
        
            # fetch any fatal errors and try to reconnect to the server
            try:
                gameinfo = self.getGameInfo()
                self.revision = openttd.version.parse_version(gameinfo.server_revision)
                self.get_taginfo()
                self.joinGame()
                self.cleanup()
            except Exception, e:
                self.cleanup()
                LOG.error('main loop error: '+str(e))
                LOG.error(self.get_traceback())
            
            if self.reconnectCond:
                # sleep a second
                time.sleep(1)
    def get_traceback(self):
        errorMsg = StringIO.StringIO()
        traceback.print_exc(file=errorMsg)
        return errorMsg.getvalue()
    def get_taginfo(self):
        self.finger = openttd.version.OTTDFingerConnection()
        self.finger.close()
    def sendChat(self, msg, desttype=const.DESTTYPE_BROADCAST, dest=0, chattype=const.NETWORK_ACTION_CHAT):
        payload = structz.pack('BBIzQ', chattype, desttype, dest, msg, 0)
        try:
            self.sendMsg_TCP(const.PACKET_CLIENT_CHAT, payload)
        except Exception, e:
            LOG.error("error while sending chat: %s" % e)
            LOG.error(self.get_traceback())
        
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
        payload = structz.pack('bIIIIzB', player, command, p1, p2, tile, text, cbid)
        self.sendMsg_TCP(const.PACKET_CLIENT_COMMAND, payload)
        
    def getCompanyString(self, id, withplayers=True):
        if id == const.PLAYER_SPECTATOR:
            companystring = "spectators"
        else:
            companystring = "company %d" % (id+1)
        if not withplayers: return companystring
        
        players = []
        for client in self.playerlist:
            cl = self.playerlist[client]
            if cl['company'] == id:
                players.append(cl['name'])
        if len(players) < 4:
            return companystring + " (" + ", ".join(players) + ")"
        else:
            return companystring + " (%d players)" % (len(players))
        
    def doCallback(self, callback, arguments=[]):
        if callback in self.callbacks:
            for callback in self.callbacks[callback]:
                callback(*arguments)


    def processCommand(self, event):
        LOG.debug("processing command '%s'" % event.msg)
        command_prefix = config.get("main", "commandprefix")
        if not event.isCommand():
            return
        if not event.msg.startswith(command_prefix):
            command = event.msg
        else:
            command = event.msg[len(command_prefix):]
        if len(command) < 1:
            return
        argv = command.split()
        
        if config.has_option('irccommands', command):
            rawcommand = config.get('irccommands', command)
            if not len(rawcommand) > 0:
                return
            interpolation = {
                "frame": self.frame_server,
                "time": time.ctime().__str__(),
                "ip": self.ip,
                "port": self.port,
                "ottdversion": str(self.revision),
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
        elif argv[0] == 'notice' and not self.irc is None:
            if len(argv) != 3:
                event.respond('Usage: notice <name> <msg>')
            else:
                try:
                    name = argv[1]
                    msg = command[len(argv[0]) + len(argv[1]) + 2:]
                except:
                    event.respond("Usage: notice <name> <msg>")
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
            elif command == 'reconnect':
                payload = structz.pack('z', "%s (reconnecting)" % config.get("openttd", "quitmessage"))
                Broadcast("Reconnecting to server", parentclient=self, parent=event)
                self.sendMsg_TCP(const.PACKET_CLIENT_QUIT, payload)
            elif command.startswith("load_plugin ") and len(command) > 12:
                arg = command[12:]
                plugins.load_plugin(arg, obj=self.plugins['modules'])
                plugins.initialize_plugins(self, module=arg, obj=self.plugins['instances'])

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
        
    def startIRC(self):
        if not self.irc is None:
            return
        from irc_lib import IRCBotThread
        self.irc = IRCBotThread(self.irc_channel, config.get("irc", "nickname"), self.irc_server, self, self.irc_server_port)
        self.irc.start()
        Broadcast("loading IRC", parentclient=self)

    def stopIRC(self):
        if not self.irc is None:
            try:
                self.irc.stop(config.get("irc", "quitmessage"))
            except SystemExit:
                pass
            self.irc = None
    
    def quit(self):
        payload = structz.pack('z', config.get("openttd", "quitmessage"))
        self.reconnectCond = False
        self.sendMsg_TCP(const.PACKET_CLIENT_QUIT, payload)
        
    def handlePacket(self, command, content):
        self.doCallback("on_receive_packet", [command, content])
        if command == const.PACKET_SERVER_QUIT:
            cid, = structz.unpack('I', content)
            if cid == self.client_id:
                self.runCond = False
                LOG.info("Quit from server")
                self.doCallback("on_self_quit", [-1])

            else:
                if cid in self.playerlist:
                    IngameToIRC("%s has quit the game" % (self.playerlist[cid]['name']), parentclient=self)
                    self.doCallback("on_user_quit", [self.playerlist[cid]['name']])
            if cid in self.playerlist:
                name = self.playerlist[cid]['name']
                del self.playerlist[cid]
        elif command == const.PACKET_SERVER_ERROR:
            (errornum,) = structz.unpack('B', content)
            self.doCallback("on_self_quit", [errornum])
            if errornum in const.error_names:
                IngameToIRC("Disconnected from server: %s" % const.error_names[errornum][1], parentclient=self)
            self.runCond = False
        
        elif command == const.PACKET_SERVER_ERROR_QUIT:
            cid, errornum = structz.unpack('IB', content)
            if cid == self.client_id:
                self.doingloop = False
                self.doCallback("on_self_quit", [errornum])
                LOG.info("Disconnected from server")
            if cid in self.playerlist:
                self.doCallback("on_user_disconnect", [self.playerlist[cid]['name'], errornum])
                IngameToIRC("%s has quit the game (%s)" % (self.playerlist[cid]['name'], const.error_names[errornum][1]), parentclient=self)
                del self.playerlist[cid]

        elif command == const.PACKET_SERVER_CLIENT_INFO:
            cid, playas, name = structz.unpack('IBz', content)
            if cid == self.client_id:
                self.playername = name
                self.playas = playas
            if cid in self.playerlist:
                if name != self.playerlist[cid]['name']:
                    IngameToIRC("%s changed nick to %s" % (self.playerlist[cid]['name'], name), parentclient=self)
                if playas != self.playerlist[cid]['company']:
                    if (playas == 255):
                        IngameToIRC("%s joined spectators." % (self.playerlist[cid]['name']), parentclient=self)
                    else:
                        IngameToIRC("%s has moved to company %d" % (self.playerlist[cid]['name'], playas + 1), parentclient=self)
            self.playerlist[cid] = {'name':name, 'company':playas, 'lastactive':-1, 'id': cid}
        
        elif command == const.PACKET_SERVER_JOIN:
            (playerid, ) = structz.unpack('I', content)
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
    
    def findPlayerByNick(self, nick):
        for client in self.playerlist:
            if self.playerlist[client]['name'] == nick:
                return self.playerlist[client]
        return None
    
    def joinGame(self):
        #construct join packet
        cversion = str(self.revision)
        self.playername =  config.get("openttd", "nickname")
        language = const.NETLANG_ANY
        network_id =  config.get("openttd", "uniqueid")
        payload = structz.pack('zzBBz', cversion, self.playername, self.playas, language, network_id)
        #print "buffer size: %d" % payload_size
        self.sendMsg_TCP(const.PACKET_CLIENT_JOIN, payload)
        self.runCond = True
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
                p = DataPacket(size, command, content)
                grfcount = p.recv_uint8()
                grfs = []
                for i in range(0, grfcount):
                    grfid, md5sum = p.recv_something('4s16s')
                    grfs.append((grfid, md5sum))
                if grfcount > 0:
                    LOG.debug("installed grfs (%d):" % len(grfs))
                    for grf in grfs:
                        LOG.debug(" %s - %s" % (grf[0].encode("hex"), grf[1].__str__().encode("hex")))
                LOG.debug("step2 - got installed GRFs, joining ...")
                self.sendMsg_TCP(const.PACKET_CLIENT_NEWGRFS_CHECKED)
            elif command == const.PACKET_SERVER_NEED_GAME_PASSWORD:
                if self.password != '':
                    LOG.info("server is password protected, sending password ...")
                    payload = structz.pack('z', self.password)
                    send.sendMsg_TCP(const.PACKET_CLIENT_GAME_PASSWORD, payload)
                else:
                    LOG.info("server is password protected, but no pass provided, exiting!")
                    self.runCond=False
                    self.reconnectCond = False
            elif command == const.PACKET_SERVER_NEED_COMPANY_PASSWORD:
                if self.cpassword != '':
                    LOG.info("company is password protected, sending password ...")
                    seed, uniqueid = struct.unpack('Iz', content)
                    ret = openttd.networking.hash_company_password(self.cpassword, uniqueid, seed)
                    payload = structz.pack('z', ret)
                    self.sendMsg_TCP(const.PACKET_CLIENT_PASSWORD, payload)
                else:
                    LOG.info("company is password protected, but no pass provided, exiting!")
                    self.runCond=False
                    self.reconnectCond=False

            elif command == const.PACKET_SERVER_WELCOME:
                LOG.info("yay, we are on the server :D (getting the map now ...)")
                
                self.client_id, self.generation_seed, self.servernetworkid = structz.unpack('IIz', content)
                
                self.socket_tcp.settimeout(600000000)
                
                downloadDone = False
                self.sendMsg_TCP(const.PACKET_CLIENT_GETMAP, structz.pack('I', self.revision.get_newgrf_version(self.finger)))
                mapsize_done = 0
                maptmp = None
                if config.getboolean("openttd", "savemap"):
                    maptmp = file(config.get("openttd", "savemapname"), 'wb')
                while not downloadDone and self.runCond:
                    size, command, content = self.receiveMsg_TCP()
                    
                    # first check if it is a command we need to run
                    self.handlePacket(command, content)
                    
                    if command == const.PACKET_SERVER_WAIT:
                        (num,) = structz.unpack('B', content)
                        Broadcast("Waiting for map download...%d in line" % num, parentclient=self)
                    
                    if command == const.PACKET_SERVER_MAP:
                        offset = 0
                        size2, (command2,) = structz.unpack_from('B', content, offset)
                        offset += size2
                        
                        if command2 == const.MAP_PACKET_START:
                            LOG.info("start downloading map!")
                            size, (framecounter, position) = structz.unpack_from('II', content, offset)
                        elif command2 == const.MAP_PACKET_NORMAL:
                            mapsize_done += size - offset
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
                
                ignoremsgs = []
                
                while self.runCond:
                    size, command, content = self.receiveMsg_TCP()
                    #print content
                    self.handlePacket(command, content)
                    if command == const.PACKET_SERVER_FRAME:
                        old_framecounter = self.frame_server
                        size, (self.frame_server, self.frame_max) = structz.unpack_from('II', content)
                        #if self.debug:
                        #    print "got frame %d, %d" % (frame_server, frame_max)
                        frameCounter += (self.frame_server - old_framecounter)
                        self.doCallback("on_frame", [self.frame_server])
                        
                    if frameCounter >= 74:
                        payload = structz.pack('I', self.frame_server)
                        #print "sending ACK"
                        self.sendMsg_TCP(const.PACKET_CLIENT_ACK, payload)
                        frameCounter=0
                    
                    if command == const.PACKET_SERVER_COMMAND:
                        p = DataPacket(size, command, content)
                        cp = DataStorageClass()
                        cp.company = p.recv_uint8()
                        cp.cmd     = p.recv_uint32()
                        cp.p1      = p.recv_uint32()
                        cp.p2      = p.recv_uint32()
                        cp.tile    = p.recv_uint32()
                        cp.text    = p.recv_str()
                        cp.callback= p.recv_uint8()
                        cp.frame   = p.recv_uint32()
                        cp.my_cmd  = p.recv_bool()

                        commandid = cp.cmd & 0xff
                        if commandid in const.command_names.keys():
                            LOG.debug("got command: %d(%s) from company %d: '%s'" % (commandid, const.command_names[commandid].__str__(), cp.company, cp.text))

                        self.doCallback("on_receive_command", [cp])
    
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
                        actionid, playerid, self_sent, msg, data = structz.unpack('BIbzQ', content)
                        self_sent = (playerid == self.client_id) or self_sent
                        if playerid in self.playerlist:
                            if not self_sent:
                                type_map = {const.NETWORK_ACTION_CHAT:"public", const.NETWORK_ACTION_CHAT_COMPANY:"team", const.NETWORK_ACTION_CHAT_CLIENT:"private"}
                                if actionid in type_map:
                                    IngameChat(msg, playerid, type=type_map[actionid], parentclient=self)
                        #LOG.debug(res.__str__())
                    self.doCallback("on_mainloop")
                if not self.reconnectCond:
                    self.stopIRC()
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
    argparser.add_option("-k", "--company-password", dest="companypassword", help="use password PASSWORD to join the company", type="string")
    argparser.add_option("-c", "--company", dest="company", help="join company COMPANY", type="int", default=const.PLAYER_SPECTATOR)
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
	argparser.print_help()
	sys.exit(0)
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
    if options.companypassword:
        cpassword = options.companypassword
    else:
        cpassword = ''
        
    return (ip, port, password, options.use_psyco, options.company, cpassword, options)

def main():
    import sys
    ip, port, password, use_psyco, company, cpassword, options = parseArgs()
        
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

    client = SpectatorClient(ip, port, True, password, company, cpassword)
    client.cmdlineoptions = options
    
    client.start()
    while client.isAlive():
        try:
            client.join(10) # wake up every 10 seconds to check for keyboardinterrupts
        except (KeyboardInterrupt, SystemExit):
            if client.isAlive():
                try:
                    client.quit()
                except Exception, e:
                    sys.exit(0)


    sys.exit(0)

if __name__ == '__main__':
    main()
