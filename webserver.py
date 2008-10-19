import string,cgi,time,traceback, threading, SocketServer, BaseHTTPServer, os.path, urllib
import SimpleHTTPServer
import ottd_config
from ottd_lib import DataStorageClass
from log import LOG
try:
    import json
except ImportError:
    import simplejson as json
try:
    import cPickle as pickle
except ImportError:
    import pickle

def content_type(filename):
    ext = filename[filename.rfind("."):].lower()
    map = SimpleHTTPServer.SimpleHTTPRequestHandler.extensions_map
    if ext in map:
        return map[ext]
    else:
        return map['']

class DataStorageJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, DataStorageClass):
            return obj.getDict()
        else:
            return json.JSONEncoder.default(self, obj)

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
    def compress(self, data):
        try:
            enc = self.headers.getheader("Accept-Encoding").split(',')
            fmt = []
            for e in enc: fmt.append(e.strip())
        except:
            fmt = []
        def encoder(data):
            return data
        format = None
        try:
            if "deflate" in fmt:
                import zlib
                encoder = zlib.compress
                format = "deflate"
        except:
            pass
        print fmt, format
        return format, encoder(data)
        

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
                self.send_error(404)
                return

            encoding, data = self.compress(output)
            self.send_response(200, "OK")
            self.send_header('Content-type', 'text/html')
            if not encoding is None:
                self.send_header('Content-Encoding', encoding)
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/data/companies":
            try:
                f = open(ottd_config.config.get("stats", "cachefilename"), 'rb')
            except IOError:
                obj = []
            else:
                obj = pickle.load(f)
                f.close()
            cls = self.server._callbackclass
            jsonoutput = json.dumps(obj, sort_keys=True, indent=4, cls=DataStorageJSONEncoder)
            encoding, data = self.compress(jsonoutput)
            
            self.send_response(200, "OK")
            self.send_header('Content-type', 'application/json')
            if not encoding is None:
                self.send_header('Content-Encoding', encoding)
            self.send_header ("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
        elif self.path == "/data/clients":
            cls = self.server._callbackclass
            
            response = json.dumps(cls.playerlist, indent=4, sort_keys=True)
            encoding, data = self.compress(response)
            self.send_response(200, "OK")
            self.send_header('Content-type', 'application/json')
            if not encoding is None:
                self.send_header('Content-Encoding', encoding)
            self.send_header ("Content-Length", len(data))
            self.end_headers()
            self.wfile.write(data)
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
                    self.send_error(500, "couldn't find template")
                    return

            if os.path.exists(fn):
                f = open(fn, "rb")
                content = f.read()
                f.close()
                encoding, data = self.compress(content)
                self.send_response (200)
                self.send_header ("Content-type", content_type(fn))
                if not encoding is None:
                    self.send_header("Content-Encoding", encoding)
                self.send_header ("Content-Length", len(data))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_error(404)
                return
            


class myWebServer(threading.Thread, SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    """
    multithreaded webserver class for openttd-python
    """
    def __init__(self, cls, port):
        """
        constructor
        @type  cls: SpectatorClient
        @param cls: class to get the data from
        @type port: int
        @param port: port to run with
        """
        self.port = port
        self._callbackclass = cls
        BaseHTTPServer.HTTPServer.__init__(self, ('', self.port), MyHandler)
        threading.Thread.__init__(self)
    def run(self):
        """
        thread entry point for the webserver
        """
        self.serve_forever()
    def stop(self):
        """
        this stops the webserver
        """
        self.server_close()