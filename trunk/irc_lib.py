import socket, time, threading, copy

class IRCSendThread(threading.Thread):
	runCond = True
	out_queue = []
	
	def __init__(self, socket, channel):
		self.socket = socket
		self.channel=channel
		self.status=False
		self.runCond=True
		threading.Thread.__init__(self)
	
	def run(self):
		print "send thread started ..."
		while self.runCond:
			time.sleep(0.5)
			if self.status:
				#print "checking: %d" %(len(self.out_queue))
				for msg in self.out_queue:
					self.socket.send ('PRIVMSG %s :%s\r\n'%(self.channel, msg))
					time.sleep(0.2)
				self.out_queue = []


class IRC(threading.Thread):
	in_queue = []
	runCond = True
	
	def __init__(self, debug=True,network='blueyonder.uk.quakenet.org', channel='#openttdserver.de', network_port=6667):
		self.network=network
		self.network_port=network_port
		self.channel=channel
		self.debug = debug
		self.sendThread = None
		threading.Thread.__init__(self)
	
	def stop(self):
		self.runCond = False
		
	def run(self):
		print "connecting ..."
		self.in_queue.append(('server', "IRC connecting"))
		#network = 'blueyonder.uk.quakenet.org'
		#network = 'irc.oftc.net'
		#self.channel = "#ap+"
		#self.channel = "#openttdserver.de"
		#port = 6667
		irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
		irc.connect ( ( self.network, self.network_port ) )
		irc.send ( 'NICK openttd-bot\r\n' )
		irc.send ( 'USER openttd-bot openttd-bot1 openttd-bot2 :Python IRC\r\n' )
		self.sendThread = IRCSendThread(irc, self.channel)
		self.sendThread.start()
		connected = False
		while self.runCond:
			data = irc.recv ( 4096 )
			
			pp = data.find ('PING')
			if pp != -1:
				msg = 'PONG ' + data[pp+5:pp+17] + '\r\n'
				#print ">>>>",msg
				irc.send ( msg )

			pp = data.find ('/QUOTE PONG')
			if pp != -1:
				msg = '/QUOTE PONG ' + data[pp+12:pp+24] + '\r\n'
				#print ">>>>",msg
				irc.send ( msg )
			
			if data.find ("End Of MOTD") != -1 or data.find ("End of /MOTD") != -1:
				irc.send ( 'JOIN %s\r\n'%self.channel )
				self.in_queue.append(('server', "IRC connected, activating chat bridge!"))
				connected=True
				
			if connected:
				#self.in_queue = []
				self.sendThread.status=True

				pp=data.find ("PRIVMSG %s :"%self.channel)
				if pp != -1:
					nickname = data[1:data.find("!")]
					msg = data[pp+len("PRIVMSG %s :"%self.channel):].strip()
					self.in_queue.append((nickname, msg))
			
			if self.debug and data.strip() != "":
				print data
		irc.close()
		
	def say(self, msg):
		if self.sendThread:
			print "add chat msg: %s, %d" %(msg, len(self.sendThread.out_queue))
			self.sendThread.out_queue.append(msg)
		
	def getSaid(self):
		list = copy.copy(self.in_queue)
		self.in_queue = []
		return list

#if __name__ == '__main__':
#	IRC().start()
