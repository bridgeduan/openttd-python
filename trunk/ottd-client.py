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
		
	def processCommand(self, msg):
		LOG.debug("processing command '%s'" % msg)
		if config.has_option('irccommands', msg[1:]):
			self.sendChat(config.get('irccommands', msg[1:]))
		elif msg == "!frame":
			self.sendChat("we are at frame number %d" % self.frame_server)
		elif msg == "!time":
			self.sendChat(time.ctime().__str__())
		elif msg in ["!address", '!port', '!ip']:
			self.sendChat("%s:%d"%(self.ip, self.port))
		elif msg == "!activeplayers":
			#clients = []
			mytime = time.time()
			counter = 0
			for clientid in self.playerlist.keys():
				this_time = mytime - self.playerlist[clientid]['lastactive']
				if this_time < 60*5:
					counter+=1
					players = []
					for clientid2 in self.playerlist.keys():
						if self.playerlist[clientid2]['company'] == self.playerlist[clientid]['company']:
							players.append(self.playerlist[clientid2]['name'])
					playerstr = ", ".join(players)
					timestr = "%d seconds ago" % (this_time)
					self.sendChat("company %d (%s) last active: %s"%(self.playerlist[clientid]['company'], playerstr, timestr))
				#clients.append[this_time] = self.playerlist[clientid]
			if counter == 0:
				self.sendChat("no companies actively playing in the last 5 minutes")
		
		if config.getint("main", "productive") == 0:
			#remove useless commands
			if msg == "!test1":
				payload = packExt('bbHz', NETWORK_ACTION_NAME_CHANGE, DESTTYPE_BROADCAST, 0, "foobar")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif msg == "!test2":
				payload = packExt('bbHz', NETWORK_ACTION_GIVE_MONEY, DESTTYPE_BROADCAST, 0, "1783424")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif msg == "!test3":
				payload = packExt('bbHz', NETWORK_ACTION_GIVE_MONEY, DESTTYPE_BROADCAST, 0, "-1783424534")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif msg == "!test4":
				payload = packExt('bbHz', NETWORK_ACTION_SERVER_MESSAGE, DESTTYPE_BROADCAST, 0, "I AM IMPOSING THE SERVER PIEP PIEP")
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_CHAT, payload_size, payload, type=M_TCP)
			elif msg == "!test5":
				CMD_PLACE_SIGN = 60
				self.sendCommand(CMD_PLACE_SIGN, 0)
			elif msg == "!test6":
				self.sendChat("Leaving", type=NETWORK_ACTION_LEAVE)
			elif msg == "!test7":
				self.sendChat("Joining", type=NETWORK_ACTION_JOIN)
			elif msg == '!quit':
				payload = packExt('z', config.get("openttd", "quitmessage"))
				payload_size = len(payload)
				self.sendMsg(PACKET_CLIENT_QUIT, payload_size, payload, type=M_TCP)
			elif msg == '!unloadirc' and not self.irc is None and config.getint("webserver", "enabled")==1:
				self.irc.stop()
				self.irc = None
				self.sendChat("IRC unloaded", type=NETWORK_ACTION_SERVER_MESSAGE)
		
		if msg == '!loadirc' and self.irc is None and config.getint("irc", "enabled")==1:
			self.irc = IRC(self, network=self.irc_network, channel=self.irc_channel)
			self.irc.start()
			self.sendChat("loading IRC", type=NETWORK_ACTION_SERVER_MESSAGE)
		elif msg == '!showplayers':
			for clientid in self.playerlist.keys():
				self.sendChat("Client #%d: %s, playing in company %d" % (clientid, self.playerlist[clientid]['name'], self.playerlist[clientid]['company']))
		elif msg == '!startwebserver' and config.getint("webserver", "enabled")==1:
			port = config.getint("webserver", "port")
			self.webserver = myWebServer(self, port)
			self.webserver.start()
			self.sendChat("webserver started on port %d"%port, type=NETWORK_ACTION_SERVER_MESSAGE)
		elif msg == '!stopwebserver' and config.getint("webserver", "enabled")==1:
			if self.webserver:
				self.webserver.stop()
				self.webserver = None
				self.sendChat("webserver stopped", type=NETWORK_ACTION_SERVER_MESSAGE)

		# cases not using if/elif
		if msg.startswith("!lastactive") and len(msg) >12:
			arg = msg[12:]
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
			res, size = unpackExt('Hz', content)
			if not res is None:
				if res[0] == self.client_id:
					self.runCond = False
			if res[0] in self.playerlist:
				self.dispatchEvent("%s has quit the game(%s)" % (self.playerlist[res[0]]['name'], res[1]), 1)
				del self.playerlist[res[0]]
		
		elif command == PACKET_SERVER_ERROR:
			res = unpackFromExt('B', content, 0)[0]
			if not res is None:
				if res in error_names.keys():
					self.dispatchEvent("Disconnected from server: %s" % error_names[res][1], 1)
			self.runCond = False
		
		elif command == PACKET_SERVER_ERROR_QUIT:
			res = unpackExt('HB', content)
			if not res is None:
				if res[0] == self.client_id:
					self.doingloop = False
					LOG.info("Disconnected from server")
				if res[0] in self.playerlist:
					self.dispatchEvent("%s has quit the game(%s)" % (self.playerlist[res[0]]['name'], error_names[res[1]][1]), 1)
					del self.playerlist[res[0]]

		elif command == PACKET_SERVER_CLIENT_INFO:
			res, size = unpackExt('HBz', content)
			if not res is None:
				if res[0] == self.client_id:
					self.playername = res[2]
					self.playas = res[1]
				if res[0] in self.playerlist:
					if res[2] != self.playerlist[res[0]]['name']:
						self.dispatchEvent("%s has changed his/her nick to %s" % (self.playerlist[res[0]]['name'], res[2]), 1)
					if res[1] != self.playerlist[res[0]]['company']:
						self.dispatchEvent("%s has been moved to company %d" % (self.playerlist[res[0]]['name'], res[1]), 1)
				self.playerlist[res[0]] = {'name':res[2], 'company':res[1], 'lastactive':-1}
		
		elif command == PACKET_SERVER_JOIN:
			res = unpackFromExt('H', content, 0)[0]
			if res in self.playerlist:
				self.dispatchEvent("%s has joined the game" % self.playerlist[res]['name'], 1)
		
		if command == PACKET_SERVER_SHUTDOWN:
			self.dispatchEvent("Server shutting down...have a nice day!", 1)
			self.runCond = False
		
		if command == PACKET_SERVER_NEWGAME:
			self.dispatchEvent("Server loading new map...", 1)
			# TODO: RECONNECT
			self.runCond = False

	def joinGame(self):
		#construct join packet
		cversion = config.get("openttd", "revision") # 0.6.1
		#cversion = "r13683"
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
			if command == PACKET_SERVER_CHECK_NEWGRFS:
				offset = 0
				grfcount = unpackFromExt('B', content, offset)[0]
				offset += struct.calcsize('B')

				grfs = []
				if grfcount != 0:
					for i in range(0, grfcount):
						grfid, md5sum = unpackFromExt('4s16s', content[offset:])
						offset += struct.calcsize('4s16s')
						grfs.append((grfid, md5sum))
					LOG.debug("installed grfs (%d):" % len(grfs))
					for grf in grfs:
						LOG.debug(" %s - %s" % (grf[0].encode("hex"), grf[1].encode("hex")))
				LOG.debug("step2 - got installed GRFs, joining ...")
				self.sendMsg(PACKET_CLIENT_NEWGRFS_CHECKED, type=M_TCP)
				
			elif command == PACKET_SERVER_NEED_PASSWORD:
				if self.password != '':
					LOG.info("server is password protected, sending password ...")
					payload = packExt('Bz', NETWORK_GAME_PASSWORD, self.password)
					payload_size = len(payload)
					self.sendMsg(PACKET_CLIENT_PASSWORD, payload_size, payload, type=M_TCP)
				else:
					LOG.info("server is password protected, but no pass provided, exiting!")
					self.runCond=False
				
			elif command == PACKET_SERVER_WELCOME:
				LOG.info("yay, we are on the server :D (getting the map now ...)")
				
				res, size = unpackExt('HIz', content)
				if not res is None:
					self.client_id = res[0]
				
				self.socket_tcp.settimeout(600000000)
				
				downloadDone = False
				self.sendMsg(PACKET_CLIENT_GETMAP, type=M_TCP)
				mapsize_done = 0
				while not downloadDone:
					size, command, content = self.receiveMsg_TCP()
					
					# first check if it is a command we need to run
					self.handlePacket(command, content)
					
					if command == PACKET_SERVER_WAIT:
						res = unpackFromExt('B', content)[0]
						if not res is None:
							self.dispatchEvent("Waiting for map download...%d in line" % res, 1)
					
					if command == PACKET_SERVER_MAP:
						offset = 0
						command2 = unpackFromExt('B', content[offset:])[0]
						offset += struct.calcsize("B")
						
						if command2 == MAP_PACKET_START:
							LOG.info("starting downloading map!")
							framecounter = unpackFromExt('I', content[offset:])[0]
							offset += struct.calcsize("I")
							
							position = unpackFromExt('I', content[offset:])[0]
							offset += struct.calcsize("I")
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
				if config.getint("irc", "autojoin") == 1:
					self.processCommand("!loadirc")
				
				ignoremsgs = []
				while self.runCond:
					size, command, content = self.receiveMsg_TCP()
					#print content
					self.handlePacket(command, content)
					if command == PACKET_SERVER_FRAME:
						self.frame_server, self.frame_max = unpackFromExt('II', content)
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
						res, size = unpackExt('bIIIIzB', content)
						#print res
						if res[0] >= 0 and res[0] < MAX_COMPANIES:
							mytime = time.time()
							for c in self.playerlist.keys():
								#print res[0], self.playerlist[c]
								if self.playerlist[c]['company'] == res[0]:
									#print 'updated', self.playerlist[c]['name']
									self.playerlist[c]['lastactive'] = mytime
									
							#LOG.info("command %d from company %d"%self.playerlist[playerid]['name'])
						if res[1] in command_names.keys():
							LOG.debug("got command: %s, %s, %s" % (res[0].__str__(), command_names[res[1]].__str__(), res.__str__()))

					if command == PACKET_SERVER_CHAT:
						res, size = unpackExt('bbHz', content)
						if not res is None:
							actionid = res[0]
							playerid = res[1] # possibly wrong!
							msg = res[3]
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
								if not msg.startswith("!"):
									handlecommand = False
								if handlecommand:
									self.processCommand(msg)
								
								if not self.irc is None and len(msg) >0 and msg[0] != '|':
									self.dispatchEvent(msgtxt)

						LOG.debug(res.__str__())
						
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
							if msgtxt.strip().startswith("!"):
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
	client.password = password
	client.joinGame()
	client.disconnect()
	sys.exit(0)

if __name__ == '__main__':
	main()