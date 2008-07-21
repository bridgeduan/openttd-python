import string,cgi,time,traceback, threading, SocketServer, BaseHTTPServer
from log import *

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		#print self.path
		if self.path == "/":
			cls = self.server._callbackclass
			playerlist = "no information availabe, please check back later"
			print cls
			if not cls is None:
				playerlist=""
				for clientid in cls.playerlist.keys():
					playerlist+= "Client #%d: %s, playing in company %d\n" % (clientid, cls.playerlist[clientid]['name'], cls.playerlist[clientid]['company'])
				
			content= """
<HTML><BODY>
<h1>OpenTTD python bot</h1>
<pre>
%s
</pre>
</BODY>
</HTML>
			""" % playerlist
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(content)

class myHTTPServer(BaseHTTPServer.HTTPServer):
	def __init__(self, addr, handlerClass, cls):
		"""
		constructor
		@type  cls: SpectatorClient
		@param cls: class to get the data from
		"""
		BaseHTTPServer.HTTPServer.__init__(self, addr, handlerClass)
		self._callbackclass = cls

	
class myWebServer(threading.Thread):
	"""
	webserver that display the currently connected clients
	"""
	def __init__(self, cls, port):
		"""
		constructor
		@type  cls: SpectatorClient
		@param cls: class to get the data from
		@type  port: number
		@param port: the port on which to start the webserver
		"""
		self.cls = cls
		self.port = port
		threading.Thread.__init__(self)
	
	def run(self):
		"""
		thread entry point for the webserver
		"""
		LOG.debug('started httpserver...')
		self.server = myHTTPServer(('', self.port), MyHandler, self.cls)
		self.server.serve_forever()

	def stop(self):
		"""
		this stops the webserver
		"""
		self.server.server_close()

