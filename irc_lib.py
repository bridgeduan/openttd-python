import socket, time, threading, copy
from log import *
from ottd_config import *

class IRCSendThread(threading.Thread):
	"""
	This class will be used to sent data to the active IRC connection
	"""
	runCond = True
	out_queue = []
	
	def __init__(self, socket, channel):
		"""
		constructor
		@type  socket: socket
		@param socket: the socket that already got connected to the IRC server
		@type  channel: string
		@param channel: the name of the channel to join
		"""
		self.socket = socket
		self.channel=channel
		self.status=False
		self.runCond=True
		threading.Thread.__init__(self)

	def __del__(self):
		self.runCond = False
		
	def run(self):
		"""
		thread entry point, called with start()
		"""
		LOG.debug("send thread started ...")
		while self.runCond:
			time.sleep(0.5)
			self.dequeue()
			#print "checking: %d" %(len(self.out_queue))
	
	def dequeue(self):
		# todo: add real flow control checking
		if self.status:
			for msg in self.out_queue:
				time.sleep(0.2)
				
				txt = msg[0]
				type = msg[1]
				if type == 1:
					self.socket.send ('PRIVMSG %s :\001ACTION | %s\001\r\n'%(self.channel, txt))
				else:
					self.socket.send ('PRIVMSG %s :%s\r\n'%(self.channel, txt))

			self.out_queue = []

	
		


class IRC(threading.Thread):
	"""
	This class provides a connection to an IRC server and the ability to read and write string from and to it
	"""
	in_queue = []
	runCond = True
	
	def __init__(self, network='blueyonder.uk.quakenet.org', channel='#openttdserver.de', network_port=6667, botname='openttd-bot'):
		"""
		constructor
		@type  network: string
		@param network: the hostname/ip of the IRC server to connect to
		@type  channel: string
		@param channel: the name of the channel to join
		@type  network_port: number
		@param network_port: the port where the server listens
		@type  botname: string
		@param botname: name of the bot to join IRC
		"""
		self.network=network
		self.botname=botname
		self.network_port=network_port
		self.channel=channel
		self.sendThread = None
		threading.Thread.__init__(self)

	def stop(self):
		"""
		this disconnects from IRC
		@todo: add proper disconnectionm, atm its only timing out
		"""
		if self.sendThread:
			self.sendThread.dequeue()

		self.runCond = False
		
	def run(self):
		"""
		thread entry point, called with start()
		"""
		LOG.info("IRC| IRC connecting ...")
		self.in_queue.append(('server', "IRC connecting", 0))
		#network = 'blueyonder.uk.quakenet.org'
		#network = 'self.irc.oftc.net'
		#self.channel = "#ap+"
		#self.channel = "#openttdserver.de"
		#port = 6667
		self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		self.irc.connect ( ( self.network, self.network_port ) )
		self.irc.send ( 'NICK %s\r\n'%self.botname )
		self.irc.send ( 'USER %s %s1 %s2 :Python IRC\r\n'%(self.botname,self.botname,self.botname) )
		self.sendThread = IRCSendThread(self.irc, self.channel)
		self.sendThread.start()
		connected = False
		while self.runCond:
			try:
				data = self.irc.recv ( 4096 )
			except:
				continue
			if len(data.strip()) == 0:
				continue
			
			pp = data.find ('PING')
			if pp != -1:
				msg = 'PONG ' + data[pp+5:pp+17] + '\r\n'
				#print ">>>>",msg
				self.irc.send ( msg )

			pp = data.find ('/QUOTE PONG')
			if pp != -1:
				msg = '/QUOTE PONG ' + data[pp+12:pp+24] + '\r\n'
				#print ">>>>",msg
				self.irc.send ( msg )
			
			if data.find ("End Of MOTD") != -1 or data.find ("End of /MOTD") != -1:
				self.irc.send ( 'JOIN %s\r\n'%self.channel )
				self.in_queue.append(('server', "IRC connected, activating chat bridge!", 0))
				connected=True
				
			if connected:
				#self.in_queue = []
				if not self.sendThread.status:
					self.sendThread.status=True
					LOG.debug("IRC| we are connected!")
					self.irc.settimeout(2)

				pp=data.find ("PRIVMSG %s :"%self.channel)
				if pp != -1:
					nickname = data[1:data.find("!")]
					type=0
					msg = data[pp+len("PRIVMSG %s :"%self.channel):].strip()
					if msg.startswith("\001ACTION"):
						msg = msg.replace("\001", "")
						msg = msg.replace("ACTION", "")
						msg = msg.strip()
						type=1
					self.in_queue.append((nickname, msg, type))
			
			if data.strip() != "":
				LOG.debug("IRC| %s" % data)		
		
		self.irc.send ( 'QUIT :%s\r\n'%config.get("irc", "quitmessage"))
		self.irc.close()
		
	def say(self, msg, type):
		"""
		called to sent something to IRC
		@type  msg: string
		@param msg: string to say
		"""
		if self.sendThread:
			LOG.debug("add chat msg: %s, %d" %(msg, len(self.sendThread.out_queue)))
			self.sendThread.out_queue.append((msg, type))
		
	def getSaid(self):
		"""
		called to get message queue
		@rtype:  list
		@return: list with things said
		"""
		list = copy.copy(self.in_queue)
		self.in_queue = []
		return list
