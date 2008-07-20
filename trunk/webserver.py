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
				for client in cls.playerlist:
					playerlist+= "Client #%d: %s, playing in company %d\n" % (client, cls.playerlist[client][0], cls.playerlist[client][1])
				
			content= """
<HTML><BODY>
<h1>Openttd Client Webserver</h1>
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
        BaseHTTPServer.HTTPServer.__init__(self, addr, handlerClass)
        self._callbackclass = cls

	
class myWebServer(threading.Thread):
	def __init__(self, cls, port):
		self.cls = cls
		self.port = port
		threading.Thread.__init__(self)
	
	def run(self):
		LOG.debug('started httpserver...')
		server = myHTTPServer(('', self.port), MyHandler, self.cls)
		server.serve_forever()



