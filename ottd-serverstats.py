#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
import time, sys
from operator import itemgetter

from ottd_lib import M_UDP, Client
from ottd_config import config
from ottd_grfs import GrfDB
import ottd_constants as const
VERBOSE = config.getboolean("serverstats", "verbose")
SERVERS = {}
GRFS = GrfDB()
SVNREVISION = "$Rev$"

class Grf:
	def __init__(self, id, md5, name):
		self.grfid = id
		self.usedcount = 0
		self.totalclients = 0
		self.name = name
		self.md5sum = md5
		self.servers = []
	def addServer(self, server):
		self.usedcount += 1
		self.totalclients += server.clients_on
		self.servers.append(server)
	def getUsedPercent(self, totalcount):
		return float(self.usedcount)/float(totalcount)*100
	def __cmp__(self, other):
		return cmp(self.usedcount, other.usedcount)
		


class ClientGameInfo(Client):
	# this class implements the thread start method
	def run(self):
		self.connect(M_UDP)
		if len(self.errors) == 0:
			self.socket_udp.settimeout(10)
			info = self.getGameInfo()
			SERVERS[self.ip + ":%d" % self.port] = info
			if not info is None:
				info.ip = self.ip
				info.port = self.port
				info.newgrfs = []
				unknowngrfs = None
				if len(info.grfs) != 0:
					unknowngrfs = GRFS.getgrfsnotinlist(info.grfs)
					if len(unknowngrfs) != 0:
						unknowngrfs = self.getGRFInfo(unknowngrfs)
					for grf in info.grfs:
						if not GRFS.hasgrf(grf[1]) and not unknowngrfs is None:
							GRFS.addgrfinlist(unknowngrfs, grf[0])
						info.newgrfs.append((grf[0], grf[1], GRFS.getgrfname(grf)))
		else:
			SERVERS[self.ip + ":%d" % self.port] = ", ".join(self.errors)
		self.disconnect()

def savestatstofile(filename="serverstats.bin", servers=[]):
	if not config.getboolean("serverstats", "savehistory"):
		return
	t = time.time()
	try:
		import pickle
	except ImportError:
		LOG.error("error while loading the pickle module...")
		return
	try:
		f = open(filename, 'rb')
		oldstats = pickle.load(f)
		f.close()
	except IOError:
		oldstats = {}
	oldstats[t] = servers
	try:
		f = open(filename, 'wb')
		pickle.dump(oldstats, f)
		f.close()
	except IoError:
		LOG.error("error while saving history file!")

def main():
	# get the server list
	client_master = Client(const.NETWORK_MASTER_SERVER_HOST, const.NETWORK_MASTER_SERVER_PORT, False)
	client_master.connect(M_UDP)
	servers = client_master.getServerList()
	client_master.disconnect()
	
	# query the servers
	GRFS.loadfromfile("newgrfs.grflist")
	counter = 0
	for server in servers:
		counter += 1
		client = ClientGameInfo(server[0], server[1], False, counter)
		client.start()
		
	t = time.time()
	ln=0
	#time.time() - t < 5
	while len(SERVERS.keys()) < len(servers):
		if VERBOSE:
			if abs(len(SERVERS.keys()) - ln) > 10:
				print "%3d/%3d servers queried, % 6.2f %%" % (len(SERVERS.keys()), len(servers), (float(len(SERVERS.keys()))/float(len(servers)))*100.0)
				ln = len(SERVERS.keys())
	
	
	# save the grf list if it is changed
	GRFS.savetofile("newgrfs.grflist")
	savestatstofile(servers=SERVERS)
	
	# start processing the data
	counters={}
	servererr=0
	counters["server_revision"] = {} # server revision
	counters["server_lang"] = {} # language
	counters["map_name"] = {} # map
	counters["map_size"] = {} # map-size
	counters["map_set"] = {} # landscape
	used_grfs = {}
	grfcount = 0
	myottdservers = 0
	newgrf_servers = 0
	newgrf_clients = 0
	
	for k in SERVERS.keys():
		if type(SERVERS[k]) == type(""):
			servererr+=1
			if VERBOSE:
				print "%3d: ERROR: %s" % (k, SERVERS[k])
			continue
		if not SERVERS[k] is None:
			server = SERVERS[k]
			#if VERBOSE:
			#	print "%3d: %s"%(k,server.__str__())
			for i in ["server_count","game_date","start_date","companies_max","companies_on","spectators_max","use_password","clients_max","clients_on","spectators_on","dedicated"]:
				if not i in counters.keys():
					counters[i] = 0
				if i == "server_count":
					counters[i] += 1
				else:
					counters[i] += getattr(server, i)
			
			# handle list fields
			for i in ["server_revision","server_lang","map_name","map_size","map_set"]:
				if i == "map_size":
					key = "%5d x %-5d" % (server.map_width, server.map_height)
				else:
					key = getattr(server, i)
				if not key in counters[i].keys():
					# 0 = counter
					# 1 = client counter
					counters[i][key] = [0, 0]
				counters[i][key][0] += 1
				counters[i][key][1] += server.clients_on
			
			if server.server_name.find("myottd.net") >= 0:
				myottdservers += 1
				
			# grf stats
			grfs = SERVERS[k].newgrfs
			for grf in grfs:
				grfname = grf[1]
				if not grfname in used_grfs:
					used_grfs[grfname] = Grf(grf[0], grf[1], grf[2])
				used_grfs[grfname].addServer(server)
				grfcount += 1
				
			# calculate amount of newgrf servers
			if len(grfs) > 0:
				valid = True
				if len(grfs) == 1:
					if grfs[0][0].encode('hex') == '52570103': #ignore generic tram GRF
						valid = False
				if valid:
					newgrf_servers += 1
					newgrf_clients += server.clients_on
	def percent(value1, value2=counters["server_count"]):
		return float(value1)/float(value2)*100
	if VERBOSE:
		print '#'*79
	print "OpenTTD Server statistics (%s):" % time.ctime()
	print "the master server currently knows %d servers, %d are up, %d could be queried" % (len(SERVERS.keys()), len(SERVERS.keys()) - servererr, counters["server_count"])
	print "there are currently %d clients online, a maximum of %d can be online (%.2f%%)" % (counters["clients_on"], counters["clients_max"], percent(counters["clients_on"], counters["clients_max"]))
	print "companies: %d / %d (%.2f%%)" % (counters["companies_on"], counters["companies_max"], percent(counters["companies_on"], counters["companies_max"]))
	print "spectators: %d / %d (%.2f%%)" % (counters["spectators_on"], counters["spectators_max"], percent(counters["spectators_on"], counters["spectators_max"]))
	print "%3d of %3d servers have a password               (%.2f%%)" % (counters["use_password"], counters["server_count"], percent(counters["use_password"]))
	print "%3d of %3d servers are dedicated                 (%.2f%%)" % (counters["dedicated"], counters["server_count"], percent(counters["dedicated"]))
	print "%3d of %3d servers have newgrfs                  (%.2f%%)" % (newgrf_servers, counters["server_count"], percent(newgrf_servers))
	print "%3d of %3d players are playing on newgrf servers (%.2f%%)" % (newgrf_clients, counters["clients_on"], percent(newgrf_clients, counters["clients_on"]))
	print "%3d of %3d servers are hosted by myottd.net      (%.2f%%)" % (myottdservers, counters["server_count"], percent(myottdservers))
	
	
	print ""
	print "used versions:"
	for item in sorted(counters["server_revision"].items(), key=itemgetter(1), reverse=True):
		print " % 16s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], percent(item[1][0]), item[1][1])
	
	print ""
	print "used map sizes:"
	for item in sorted(counters["map_size"].items(), key=itemgetter(1), reverse=True):
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], percent(item[1][0]), item[1][1])
		
	print ""
	print "used languages:"
	for item in sorted(counters["server_lang"].items(), key=itemgetter(1), reverse=True):
		if item[0] <= len(const.known_languages):
			langstr = const.known_languages[item[0]]
		else:
			langstr = "unkown language: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (langstr, item[1][0], percent(item[1][0]), item[1][1])
	
	print ""
	print "used landscapes:"
	landscapes = ['normal', 'arctic', 'tropic', 'toyland']
	for item in  sorted(counters["map_set"].items(), key=itemgetter(1), reverse=True):
		if item[0] < 4:
			lcs = landscapes[item[0]]
		else:
			lcs = "unkown landscape: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (lcs, item[1][0], percent(item[1][0]), item[1][1])
		
	print ""
	print "used maps:"
	for item in sorted(counters["map_name"].items(), key=itemgetter(1), reverse=True):
		print " % 50s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], percent(item[1][0]), item[1][1])

	print ""
	print "used GRFs (%d used, %d unique known, %d in database):" % (grfcount, len(used_grfs), GRFS.getdbcount())
	for item in sorted(used_grfs.values(), reverse=True):
		print "% 52s: %3d (% 5.1f%%), %3d clients" % (item.name[:52], item.usedcount, item.getUsedPercent(grfcount), item.totalclients)
	
	print ""
	print "Generated by openttd-python serverstats r" + SVNREVISION.strip('$').split(':')[-1].strip()
	sys.exit(0)

if __name__ == '__main__':
	main()
