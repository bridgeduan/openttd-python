import string,cgi,time,traceback, threading, SocketServer, BaseHTTPServer, os.path, urllib
from log import *

ext2conttype = {"jpg": "image/jpeg",
                "jpeg": "image/jpeg",
                "png": "image/png",
                "gif": "image/gif",
                "html": "text/html",
                "htm": "text/html",
                "swf": "application/x-shockwave-flash",
				"xml": "text/xml",
				}
def content_type(filename):
	ext = filename[filename.rfind(".")+1:].lower()
	if ext in ext2conttype.keys():
		return ext2conttype[ext]
	else:
		return "text/html"


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	
	def loadTemplate(self, name):
		basedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
		fn = os.path.normpath(os.path.join(basedir, name.lstrip('/')))
		if os.path.exists(fn):
			f = open(fn, "r")
			fc = f.read()
			f.close()
			return fc
		else:
			return None
			
	def updateChartData(self):
		chart_template = self.loadTemplate('stats_money_template.xml')
		if chart_template is None:
			return
		cls = self.server._callbackclass
		LOG.debug('updating chart xml data...')
		chartData=""
		print len(cls.stats)
		
		# legend
		chartData+="<row>\n\t<null/>\n"
		for stat in cls.stats:
			gameinfo = stat[0]
			chartData+="\t<number>%d</number>\n" % gameinfo['game_date']
		chartData+="</row>\n"
		
		# real data
		companies = len(cls.stats[0][1])
		for company in range(0, companies):
			chartData+="<row>\n\t<string>Company %d</string>\n"%company
			for stat in cls.stats:
				companies_data = stat[1]
				if len(companies_data)-1 >= company:
					money = companies_data[company]['money']
					chartData+="\t<number>%f</number>\n"%money
			chartData+="</row>\n"
		
		basedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
		f = open(os.path.join(basedir, 'stats_money.xml'), "w")
		f.write(chart_template%{'chartdata':chartData})
		f.close()

	def sendError(self, num=404):
		txt = """\
			<html>
			   <head><title>404 file not found</title></head>
			   <body>404 file not found</body>
			</html>\n""" 
		self.send_response(num)
		self.send_header("Content-type", "text/html")
		self.send_header("Content-Length", str (len (txt)))
		self.end_headers()
		self.wfile.write(txt)

	def do_GET(self):
		#print self.path
		self.path = urllib.quote (urllib.unquote (self.path))
		basedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')
		#print self.path
		
		self.updateChartData()
		
		if self.path == "/":
			cls = self.server._callbackclass
			
			content = "running on %s:%d<p/>" % (cls.ip, cls.port)

			
			playerlist = "no information availabe, please check back later<p/>"
			if not cls is None:
				playerlist="<ul>"
				for clientid in cls.playerlist.keys():
					playerlist+= "<li>Client #%d: %s, playing in company %d</li>" % (clientid, cls.playerlist[clientid]['name'], cls.playerlist[clientid]['company'])
				playerlist+="</ul>"
			content += playerlist

			template = self.loadTemplate("index.html")
			if not template is None:
				output = template % { 
					'content':content,
					'server_ip': cls.ip,
					'server_port': cls.port,
					}
			else:
				self.sendError()
				return

			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			self.wfile.write(output)
		else:
			path = urllib.unquote(self.path)
			if path.find("?") >= 0:
				path = path[:path.find("?")]
			fn = os.path.normpath(os.path.join(basedir, path.lstrip('/')))
			#print path, fn
			if os.path.isdir(fn):
				newindex = os.path.join(fn,'index.html')
				if os.path.isfile(newindex):
					fn = newindex
				else:
					self.sendError()
					return

			if os.path.exists(fn):
				self.send_response (200)
				self.send_header ("Content-type", content_type(fn))
				self.send_header ("Content-Length", os.path.getsize(fn))
				self.end_headers()
				f = open(fn, "rb")
				self.wfile.write(f.read())
				f.close()
			else:
				self.sendError()
				return
			


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

