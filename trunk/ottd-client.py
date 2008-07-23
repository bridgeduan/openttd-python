from ottd_lib import *
from irc_lib import *
from webserver import *
from ottd_config import *

class BasicFileLogger:
	def __init__(self, file = "log.log"):
		self.file = file
		self.filehandle = open(file, 'a')
	def log(self, message, flush = True):
		self.filehandle.write(time.ctime().__str__() + ': ' + message + "\n")
		if flush:
			self.filehandle.flush()

class SpectatorClient(Client):
	irc = None
	irc_network = config.get("irc", "server")
	irc_channel = config.get("irc", "channel")
	playerlist = {}
	webserver = None
	
	# this class implements the thread start method
	def run(self):
		self.connect()
		if len(self.errors) == 0:
			SERVERS[self.number] = self.getGameInfo()
		else:
			SERVERS[self.number] = ", ".join(self.errors)
		self.disconnect()
	
	def dispatchEvent(self, message, type=0, irc=True):
		if irc and not self.irc is None:
			self.irc.say(message, type)
		LOG.info(message)

	def sendChat(self, msg, player = -1, type=NETWORK_ACTION_CHAT, relayToIRC=False, strtype=2):
		# sent to ottd server
		payload = packExt('bbHz', type, DESTTYPE_BROADCAST, 0, msg)
		payload_size = len(payload)
		self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
		
		#sent to irc and log
		self.dispatchEvent(msg, strtype, irc=relayToIRC)
		
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
		cbid=0
		player = self.playas
		payload = packExt('bIIIIzB', player, command, p1, p2, tile, text, cbid)
		payload_size = len(payload)
		self.sendMsg(PACKET_CLIENT_COMMAND, payload_size, payload, type=M_TCP)
		
	def getCompanyString(self, id, withplayers=True):
		if withplayers:
			players = []
			for clientid2 in self.playerlist.keys():
				if self.playerlist[clientid2]['company'] == id:
					players.append(self.playerlist[clientid2]['name'])
		if id == PLAYER_SPECTATOR:
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
		
	def processCommand(self, msg):
		LOG.debug("processing command '%s'" % msg)
		if not msg.startswith(config.get("main", "commandprefix")):
			return
		command = msg[1:]
		if config.has_option('irccommands', command):
			rawcommand = config.get('irccommands', command)
			if not len(rawcommand) > 0:
				return
			interpolation = {
				"frame": self.frame_server,
				"time": time.ctime().__str__(),
				"ip": self.ip,
				"port": self.port,
			}
			command = rawcommand % interpolation
			if len(command) > 0:
				self.sendChat(command)
		#elif command == "frame":
		#	self.sendChat("we are at frame number %d" % self.frame_server)
		#elif command == "time":
		#	self.sendChat(time.ctime().__str__())
		#elif command in ["address", 'port', 'ip']:
		#	self.sendChat("%s:%d"%(self.ip, self.port))
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
					self.sendChat("%s last active: %s"%(compstr, playerstr, timestr))
				#clients.append[this_time] = self.playerlist[clientid]
			if counter == 0:
				self.sendChat("no companies actively playing in the last 5 minutes")
		
		if not config.getboolean("main", "productive"):
			#remove useless commands
			if command == "test1":
				payload = packExt('bbHz', NETWORK_ACTION_NAME_CHANGE, DESTTYPE_BROADCAST, 0, "foobar")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif command == "test2":
				payload = packExt('bbHz', NETWORK_ACTION_GIVE_MONEY, DESTTYPE_BROADCAST, 0, "1783424")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif command == "test3":
				payload = packExt('bbHz', NETWORK_ACTION_GIVE_MONEY, DESTTYPE_BROADCAST, 0, "-1783424534")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif command == "test4":
				payload = packExt('bbHz', NETWORK_ACTION_SERVER_MESSAGE, DESTTYPE_BROADCAST, 0, "I AM IMPOSING THE SERVER PIEP PIEP")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif command == "test5":
				CMD_PLACE_SIGN = 60
				self.sendCommand(CMD_PLACE_SIGN, 0)
			elif command == "test6":
				self.sendChat("Leaving", type=NETWORK_ACTION_LEAVE)
			elif command == "test7":
				self.sendChat("Joining", type=NETWORK_ACTION_JOIN)
			elif command == 'quit':
				payload = packExt('z', config.get("openttd", "quitmessage"))
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_QUIT, payload_size, payload, type=M_TCP)
			elif command == 'reloadconfig':
				LoadConfig()
				self.dispatchEvent("Reloading config file...")
			elif command == 'unloadirc' and not self.irc is None:
				self.irc.stop()
				self.irc = None
				self.sendChat("IRC unloaded", type=NETWORK_ACTION_SERVER_MESSAGE)
		
		if command == 'loadirc' and self.irc is None and config.getboolean("main", "enableirc")==1:
			self.irc = IRC(self, network=self.irc_network, channel=self.irc_channel)
			self.irc.start()
			self.sendChat("loading IRC", type=NETWORK_ACTION_SERVER_MESSAGE)
		elif command == 'showplayers':
			for clientid in self.playerlist.keys():
				self.sendChat("Client #%d: %s, playing in %s" % (clientid, self.playerlist[clientid]['name'], self.getCompanyString(self.playerlist[clientid]['company'], False)))
		elif command == 'startwebserver' and config.getboolean("main", "enablewebserver"):
			port = config.getint("webserver", "port")
			self.webserver = myWebServer(self, port)
			self.webserver.start()
			self.sendChat("webserver started on port %d"%port, type=NETWORK_ACTION_SERVER_MESSAGE)
		elif command == 'stopwebserver':
			if self.webserver:
				self.webserver.stop()
				self.webserver = None
				self.sendChat("webserver stopped", type=NETWORK_ACTION_SERVER_MESSAGE)

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
				self.sendChat("company unkown")
			else:
				ltime = 0
				for clientid in self.playerlist.keys():
					if self.playerlist[clientid]['company'] == companyid and self.playerlist[clientid]['lastactive'] > ltime:
						ltime = self.playerlist[clientid]['lastactive']
				if ltime <=0:
					timestr = " unkown"
				else:
					timestr = "%d seconds ago" % (time.time()-ltime)
				self.sendChat("company %d last active: %s"%(companyid, timestr))
		
	
	def handlePacket(self, command, content):
		if command == PACKET_SERVER_QUIT:
			[cid, msg], size = unpackExt('Hz', content)
			if cid == self.client_id:
				self.runCond = False
			if cid in self.playerlist:
				self.dispatchEvent("%s has quit the game(%s)" % (self.playerlist[cid]['name'], msg), 1)
				del self.playerlist[cid]
		
		elif command == PACKET_SERVER_ERROR:
			[errornum], size = unpackFromExt('B', content, 0)
			if errornum in error_names.keys():
				self.dispatchEvent("Disconnected from server: %s" % error_names[errornum][1], 1)
			self.runCond = False
		
		elif command == PACKET_SERVER_ERROR_QUIT:
			[cid, errornum], size = unpackExt('HB', content)
			if cid == self.client_id:
				self.doingloop = False
				LOG.info("Disconnected from server")
			if cid in self.playerlist:
				self.dispatchEvent("%s has quit the game(%s)" % (self.playerlist[cid]['name'], error_names[errornum][1]), 1)
				del self.playerlist[cid]

		elif command == PACKET_SERVER_CLIENT_INFO:
			[cid, playas, name], size = unpackExt('HBz', content)
			if cid == self.client_id:
				self.playername = name
				self.playas = playas
			if cid in self.playerlist:
				if name != self.playerlist[cid]['name']:
					self.dispatchEvent("%s has changed his/her nick to %s" % (self.playerlist[cid]['name'], name), 1)
				if playas != self.playerlist[cid]['company']:
					self.dispatchEvent("%s has been moved to company %d" % (self.playerlist[cid]['name'], playas), 1)
			self.playerlist[cid] = {'name':name, 'company':playas, 'lastactive':-1}
		
		elif command == PACKET_SERVER_JOIN:
			[playerid], size = unpackFromExt('H', content, 0)
			if playerid in self.playerlist:
				self.dispatchEvent("%s has joined the game" % self.playerlist[playerid]['name'], 1)
		
		if command == PACKET_SERVER_SHUTDOWN:
			self.dispatchEvent("Server shutting down...have a nice day!", 1)
			self.runCond = False
		
		if command == PACKET_SERVER_NEWGAME:
			self.dispatchEvent("Server loading new map...", 1)
			# TODO: RECONNECT
			self.runCond = False

	def joinGame(self):
		#construct join packet
		cversion = self.revision
		self.playername =  config.get("openttd", "nickname")
		password = 'citrus'
		self.playas = PLAYER_SPECTATOR
		language = NETLANG_ANY
		network_id =  config.get("openttd", "uniqueid")
		payload = packExt('zzBBz', cversion, self.playername, self.playas, language, network_id)
		payload_size = len(payload)
		#print "buffer size: %d" % payload_size
		self.sendMsg(PACKET_CLIENT_JOIN, payload_size, payload, type=M_TCP)
		self.runCond=True
		while self.runCond:
			size, command, content = self.receiveMsg_TCP()
			LOG.debug("got command %s" % packet_names[command])
			if command == PACKET_SERVER_FULL:
				LOG.info("Couldn't join server...it's full. Exiting!")
				self.runCond=False
			if command == PACKET_SERVER_BANNED:
				LOG.info("Couldn't join server...banned from it. Exiting!")
				self.runCond=False
			if command == PACKET_SERVER_CHECK_NEWGRFS:
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
				self.sendMsg(PACKET_CLIENT_NEWGRFS_CHECKED, type=M_TCP)
				
			elif command == PACKET_SERVER_NEED_PASSWORD:
				[type,seed,uniqueid], size = unpackExt('BIz', content)
				if type == NETWORK_GAME_PASSWORD:
					if self.password != '':
						LOG.info("server is password protected, sending password ...")
						payload = packExt('Bz', NETWORK_GAME_PASSWORD, self.password)
						payload_size = len(payload)
						self.sendMsg(PACKET_CLIENT_PASSWORD, payload_size, payload, type=M_TCP)
					else:
						LOG.info("server is password protected, but no pass provided, exiting!")
						self.runCond=False
				elif type == NETWORK_COMPANY_PASSWORD:
					#if self.password != '':
					#salted_password=""*32
					#password="apassword"
					#for i in range(1,32):
					#	salted_password[i] = int(password[i]) ^ uniqueid[i] ^ (seed >> i)
					#	LOG.info(i)
					#LOG.info(salted_password)
					#else:
					LOG.info("company is password protected, not supported, exiting!")
					self.runCond=False

				
			elif command == PACKET_SERVER_WELCOME:
				LOG.info("yay, we are on the server :D (getting the map now ...)")
				
				[self.client_id, self.generation_seed, self.servernetworkid], size = unpackExt('HIz', content)
				
				self.socket_tcp.settimeout(600000000)
				
				downloadDone = False
				self.sendMsg(PACKET_CLIENT_GETMAP, type=M_TCP)
				mapsize_done = 0
				while not downloadDone:
					size, command, content = self.receiveMsg_TCP()
					
					# first check if it is a command we need to run
					self.handlePacket(command, content)
					
					if command == PACKET_SERVER_WAIT:
						[num], res = unpackFromExt('B', content)
						self.dispatchEvent("Waiting for map download...%d in line" % num, 1)
					
					if command == PACKET_SERVER_MAP:
						offset = 0
						[command2], size2 = unpackFromExt('B', content[offset:])
						offset += size2
						
						if command2 == MAP_PACKET_START:
							LOG.info("starting downloading map!")
							[framecounter], size2 = unpackFromExt('I', content[offset:])
							offset += size2
							
							[position], size2 = unpackFromExt('I', content[offset:])
							offset += size2
						elif command2 == MAP_PACKET_NORMAL:
							mapsize_done += size
							if int(mapsize_done / 1024) % 100 == 0:
								LOG.debug("got %d kB ..." % (mapsize_done / 1024))
						elif command2 == MAP_PACKET_END:
							LOG.info("done downloading map!")
							downloadDone=True
				
				self.sendMsg(PACKET_CLIENT_MAP_OK, type=M_TCP)
				
				# main loop, disable the timeout
				#self.socket_tcp.settimeout(600000000)
				frameCounter=73
				self.frame_server=0
				self.frame_max=0
				
				# init IRC bridge
				self.irc = None
				
				#self.sendChat("hey i am a bot :|")
				
				# auto start IRC
				if config.getboolean("irc", "autojoin"):
					self.processCommand(config.get("main", "commandprefix") + "loadirc")
				
				ignoremsgs = []
				while self.runCond:
					size, command, content = self.receiveMsg_TCP()
					#print content
					self.handlePacket(command, content)
					if command == PACKET_SERVER_FRAME:
						[self.frame_server, self.frame_max], size = unpackFromExt('II', content)
						#if self.debug:
						#	print "got frame %d, %d" % (frame_server, frame_max)
						frameCounter += 1
						
					if frameCounter >= 74:
						payload = packExt('I', self.frame_server)
						payload_size = len(payload)
						#print "sending ACK"
						self.sendMsg(PACKET_CLIENT_ACK, payload_size, payload, type=M_TCP)
						frameCounter=0

						
					if command == PACKET_SERVER_COMMAND:
						[player, command2, p1, p2, tile, text, callback, frame, my_cmd], size = unpackFromExt('BIIIIzBIB', content)

						commandid = command2 & 0xff
						#print commandid
						if commandid in command_names.keys():
							LOG.debug("got command: %d(%s) from company %d: '%s'" % (commandid, command_names[commandid].__str__(), player, text))

						#print player, command2, p1, p2, tile, text, callback, frame, my_cmd
	
						# some example  implementation
						companystr = self.getCompanyString(player)
						if commandid == 61: #CMD_RENAME_SIGN
							self.sendChat("%s renames a sign: '%s'" % (companystr, text) )
						elif commandid == 46: #CMD_SET_PLAYER_COLOR
							self.sendChat("%s changed their color"%companystr)
						elif commandid == 52: #CMD_CHANGE_COMPANY_NAME
							self.sendChat("%s changed their company name to '%s'"%(companystr, text))
						elif commandid == 53: #CMD_CHANGE_PRESIDENT_NAME
							self.sendChat("%s changed their presidents name to '%s'"%(companystr, text))
						elif commandid == 43: #CMD_BUILD_INDUSTRY
							self.sendChat("%s built a new industry"%(companystr))
						elif commandid == 44: #CMD_BUILD_COMPANY_HQ
							self.sendChat("%s built their new HQ"%(companystr))
							
	
					if command == PACKET_SERVER_CHAT:
						[actionid, playerid, unused, msg], size = unpackExt('bHbz', content)
						self_sent = (playerid == self.client_id)
						if playerid in self.playerlist:
							player_name = self.playerlist[playerid]['name']
							
							if actionid == NETWORK_ACTION_CHAT:
								if self_sent:
									handlecommand = False
									msgtxt = msg
								else:
									handlecommand = True
									msgtxt = "%s: %s" % (player_name, msg)
							elif actionid == NETWORK_ACTION_CHAT_COMPANY:
								handlecommand = True
								msgtxt = "[Team] %s: %s" % (player_name, msg)
							elif actionid == NETWORK_ACTION_CHAT_CLIENT:
								handlecommand = True
								msgtxt = "[IRC_ONLY] %s: %s" % (player_name, msg)
							else:
								handlecommand = False
								msg = ""
							if handlecommand:
								self.processCommand(msg)
							
							if not self.irc is None and len(msg) >0 and msg[0] != '|':
								self.dispatchEvent(msgtxt)

						#LOG.debug(res.__str__())
						
					if not self.irc is None:
						#check if there are msgs in the IRC to say
						for msg in self.irc.getSaid():
							nickname, msgtxt, type = msg
							if type == 0:
								#normal chat
								txt_res = "%s: %s" % (nickname, msgtxt)
							elif type == 1:
								# action
								txt_res = "%s %s" % (nickname, msgtxt)
							self.sendChat(txt_res, type=NETWORK_ACTION_SERVER_MESSAGE, relayToIRC=False)
							self.processCommand(msgtxt.strip())
						

def printUsage():
	print "usage: %s <ip:port> <password>" % sys.argv[0]
	sys.exit(1)

def main():
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
	client.connect(M_BOTH)
	[gameinfo, grflist] = client.getGameInfo()
	client.revision = gameinfo[6]
	client.password = password
	client.joinGame()
	client.disconnect()
	sys.exit(0)

if __name__ == '__main__':
	main()