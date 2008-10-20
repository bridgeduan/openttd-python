# code by RoRTom, conversion to plugin by yorick
import pluginclass
from ottd_config import config, WriteConfig
from log import LOG
import time
import os
import string,cgi,traceback, threading, SocketServer, BaseHTTPServer, os.path, urllib
import SimpleHTTPServer
from openttd.datastorageclass import DataStorageClass
from ottd_client_event import Broadcast, InternalCommand
try:
    import json
except ImportError:
    import simplejson as json
try:
    import cPickle as pickle
except ImportError:
    import pickle

class StatsWriter(pluginclass.Plugin):
    interval = 120 #every two minutes
    last = 0
    def init(self):
        self.updateConfig()
        self.enable = config.getboolean('stats', 'enable')
        self.registerCallback("on_map_done", self.clearStats)
        self.registerCallback("on_mainloop", self.checkupdatestats)
    def checkupdatestats(self):
        if time.time() - self.last > self.interval:
            self.updateStats()
    def updateStats(self):
        self.last = time.time()
        if not config.getboolean('stats', 'enable'): return
        LOG.debug("updating stats...")
        tstart = time.time()
        
        fn = config.get("stats", "cachefilename")
        obj = []
        firstSave = False
        try:
            f = open(fn, 'rb')
            obj = pickle.load(f)
            f.close()
        except IOError:
            firstSave=True
            
        value = [
                self.client.getGameInfo(encode_grfs=True, short=not firstSave),
                self.client.getCompanyInfo().companies,
                tstart
                ]
        
        obj.append(value)
        
        try:
            f = open(fn, 'wb')
            #if you use python < 2.3 use this line:
            #pickle.dump(obj, f)
            pickle.dump(obj, f, 1)
            f.close()
        except IOError:
            LOG.error("error while saving stats cache file!")
        
        tdiff = time.time() - tstart
        fs = float(os.path.getsize(fn)) / float(1024)
        LOG.debug("stats updated in %0.5f seconds. File is %.2fKB big (%d lines)"%(tdiff, fs, len(obj)))
    def clearStats(self):
        if not config.getboolean('stats', 'enable'): return
        fn = config.get("stats", "cachefilename")
        try:
            os.remove(fn)
            LOG.debug("stats cleared")
        except:
            pass
    def updateConfig(self):
        configchanged = False
        if not config.has_section("stats"):
            config.add_section("stats")
            configchanged = True
        options = {
            "enable":"On",
            "cachefilename":"stats.bin",
        }
        for option in options: 
            if not config.has_option("stats", option):
                config.set("stats", option, options[option])
                configchanged = True
        if configchanged:
            WriteConfig()
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
                f = open(config.get("stats", "cachefilename"), 'rb')
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
    def log_message(self, format, *args):
        LOG.debug("[WEB]" + format%args)
class WebserverThread(SocketServer.ThreadingMixIn, threading.Thread, BaseHTTPServer.HTTPServer):
    """
    multithreaded webserver class for openttd-python
    using a seperate class so it can be started multiple times
    do not merge with the WebServer class, you'll make it a run-once webserver, because threads can only be started once
    """
    def __init__(self, client):
        self.port = config.getint("webserver", "port")
        self._callbackclass = client
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
    def server_close(self):
        self.shutdown()
class WebServer(pluginclass.Plugin):
    """
    multithreaded webserver plugin
    """
    def init(self):
        """
        constructor
        """
        self.updateConfig()
        self.webserverthread = None
        self.registerChatCommand("startwebserver", self.startWebserver)
        self.registerChatCommand("stopwebserver", self.stopWebserver)
        self.registerCallback("on_map_done", self.autoStart)
    def autoStart(self):
        if config.getboolean("webserver", "enable") and config.getboolean("webserver", "autostart"):
            InternalCommand("startwebserver", self.client)
    def updateConfig(self):
        configchanged = False
        if not config.has_section("webserver"):
            config.add_section("webserver")
            configchanged = True
        options = {
            "enable":"On",
            "autostart":"Off",
            "port":"8080"
        }
        for option in options: 
            if not config.has_option("webserver", option):
                config.set("webserver", option, options[option])
                configchanged = True
        if configchanged:
            WriteConfig()
    def startWebserver(self, event, command):
        if config.getboolean("main", "productive") and not event.isByOp():
            return
        if not config.getboolean("webserver", "enable") or not self.webserverthread is None:
            return
        LOG.debug("starting webserver ...")
        self.webserverthread = WebserverThread(self.client)
        self.webserverthread.start()
        Broadcast("webserver started on port %d"% self.webserverthread.port, parentclient=self.client, parent=event)
    def stopWebserver(self, event, command):
        if self.webserverthread is None or (config.getboolean("main", "productive") and not event.isByOp()):
            return
        LOG.debug("stopping webserver ...")
        self.webserverthread.stop()
        self.webserverthread = None
        Broadcast("webserver stopped", parentclient=self.client, parent=event)