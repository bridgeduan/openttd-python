import string,cgi,time,traceback, threading, SocketServer, BaseHTTPServer, os.path, urllib
import ottd_config
from log import *
import simplejson
import pickle

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
        elif self.path == "/data/companies":
            try:
                f = open(ottd_config.config.get("stats", "cachefilename"), 'rb')
            except IOError:
                obj = []
            else:
                obj = pickle.load(f)
                f.close()
            cls = self.server._callbackclass
            self.send_response(200)
            self.send_header('Content-type:', 'application/json')
            self.end_headers()
            jsoninput = []
            for write in obj:
                thiswrite = []
                for instance in write:
                    if type(instance) is list:
                        thislist = []
                        for listitem in instance:
                            thislist.append(listitem.getDict())
                        thiswrite.append(thislist)
                    else:
                        thiswrite.append(instance.getDict())
                    
                jsoninput.append(thiswrite)
            jsonoutput = simplejson.dumps(jsoninput, sort_keys=True, indent=4)
            self.wfile.write(jsonoutput)
        elif self.path == "/data/clients":
            cls = self.server._callbackclass
            
            response = simplejson.dumps(cls.playerlist, indent=4, sort_keys=True)
            self.send_response(200)
            self.send_header('Content-type:', 'application/json')
            self.end_headers()
            self.wfile.write(response)
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

