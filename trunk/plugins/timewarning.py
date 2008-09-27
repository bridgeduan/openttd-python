# code by RoRTom, conversion to plugin by yorick
import pluginclass
from ottd_config import config, WriteConfig
import ottd_client_event
from log import LOG
import time

class TimeWarning(pluginclass.Plugin):
    def init(self):
        self.updateConfig()
        self.doTimeWarning = config.getboolean('timewarning', 'warnings')
        self.last_timewarning = 0
        self.readTimeFile()
        self.interval = config.getint('timewarning', 'warning_interval')
        self.registerCallback("on_mainloop", self.onMainLoop)
        self.registerChatCommand("timeleft", self.timeLeft)
        self.registerChatCommand("uptime", self.upTime)
    
    def timeLeft(self, event, commandstr, recursion_depth=0):
        if self.server_start >= 0 and self.server_runtime >= 0:
            # get time left
            tl = self.server_runtime - (time.time() - self.server_start)
            if tl >= 86400:
                time_left="%0.1f days"%(tl/86400.0)
            elif tl >= 3600:
                time_left="%0.1f hours"%(tl/3600.0)
            elif tl >= 60:
                time_left="%0.0f minutes"%(tl/60.0)
            elif tl > 0:
               time_left="%0.0f seconds"%(tl)
            elif not recursion_depth > 10: # don't get infinite loops
                self.readTimeFile(forcenew = True)
                self.timeLeft(event, commandstr, recursion_depth+1) # recurse
                return
            event.respond("time left until server will restart: %s" % time_left)
            
    def upTime(self, event, commandstr):
        if self.server_start >= 0:
            # get running time
            tl = time.time() - self.server_start
            if tl >= 60*60*24: # 60 seconds each minute, 60 minutes each hour, 24 hours each day
                time_running="%0.1f days"%(tl/86400.0)
            elif tl >= 60*60:  # 60 seconds each minute, 60 minutes each hour
                time_running="%0.1f hours"%(tl/3600.0)
            elif tl >= 60:     # 60 seconds each minute
                time_running="%0.0f minutes"%(tl/60.0)
            else:
                time_running="%0.0f seconds"%(tl)
            event.respond(time_running)
    def updateConfig(self):
        configchanged = False
        if not config.has_section("timewarning"):
            config.add_section("timewarning")
            configchanged = True
        options = {
            "enable":"On",
            "starttimefile":"starttime.txt",
            "time_running":"604800",
            "warnings":"On",
            "warning_interval":"21600"
        }
        for option in options: 
            if not config.has_option("timewarning", option):
                config.set("timewarning", option, options[option])
                configchanged = True
        if configchanged:
            WriteConfig()
    
    def onMainLoop(self):
        if self.doTimeWarning and time.time() - self.last_timewarning > self.interval:
            ottd_client_event.InternalCommand("timeleft", self.client)
            self.last_timewarning = time.time()
        
    def readTimeFile(self, forcenew=False):
        timestr = ''
        try:
            f = open(config.get('timewarning', 'starttimefile'), 'r')
            timestr = f.read()
            f.close()
        except:
            LOG.error("error while reading starttimefile")
        if timestr != '' and not forcenew:
            self.server_start = int(timestr.strip())
        else:
            f = open(config.get('timewarning', 'starttimefile'), 'wb')
            f.write(str(int(time.time())))
            f.close()
            self.server_start = int(time.time())
        self.server_runtime = config.getint('timewarning', 'time_running')
        