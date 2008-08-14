#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *
VERBOSE = False
SERVERS = {}

class Grf(DataStorageClass):
	def __init__(self, name, md5):
		self.grfid = name
		self.usedcount = 0
		self.totalclients = 0
		self.md5sum = md5
		self.servers = []
	def addServer(self, server):
		self.usedcount += 1
		self.totalclients += server.clients_on
		self.servers.append(server)
	def getUsedPercent(self, totalcount):
		return float(self.usedcount)/float(totalcount)*100
	def __str__(self, grfcount):
		return " % 10s: %3d (% 5.1f%%), %3d clients" % (self.grfid.encode('hex'), self.usedcount, self.getUsedPercent(grfcount), self.totalclients)
	def __cmp__(self, other):
		return cmp(self.usedcount, other.usedcount)
	

class ClientGameInfo(Client):
	# this class implements the thread start method
	def run(self):
		self.connect()
		if len(self.errors) == 0:
			SERVERS[self.uid] = self.getGameInfo()
			if not SERVERS[self.uid] is None:
				SERVERS[self.uid].ip = self.ip
				SERVERS[self.uid].port = self.port
				#if len(SERVERS[self.uid].grfs) != 0:
				#	SERVERS[self.uid].newgrfs = self.getGRFInfo(SERVERS[self.uid].grfs)
		else:
			SERVERS[self.uid] = ", ".join(self.errors)
		self.disconnect()

def main():
	client_master = Client(NETWORK_MASTER_SERVER_HOST, NETWORK_MASTER_SERVER_PORT, False)
	client_master.connect(M_UDP)
	servers = client_master.getServerList()
	client_master.disconnect()
	
	counter = 0
	for server in servers:
		ip = server[0]
		port = server[1]
		counter += 1
		client = ClientGameInfo(ip, port, False, counter)
		client.start()
	
	t = time.time()
	ln=0
	#time.time() - t < 5
	while len(SERVERS.keys()) < len(servers):
		if VERBOSE:
			if abs(len(SERVERS.keys()) - ln) > 10:
				print "%3d/%3d servers queried, % 6.2f %%" % (len(SERVERS.keys()), len(servers), (float(len(SERVERS.keys()))/float(len(servers)))*100.0)
				ln = len(SERVERS.keys())
	
	counters={}
	sumcounter = 0
	servererr=0
	counters["server_revision"] = {} # server revision
	counters["server_lang"] = {} # language
	counters["map_name"] = {} # map
	counters["map_width"] = {} # map-size
	counters["map_set"] = {} # landscape
	used_grfs = {}
	total_grfs = {}
	grfclients = {}
	grfcount = 0
	myottdservers = 0
	newgrf_servers = 0
	newgrf_clients = 0
	clients_overall = 0
	
	for k in SERVERS.keys():
		if type(SERVERS[k]) == type(""):
			servererr+=1
			if VERBOSE:
				print "%3d: ERROR: %s" % (k, SERVERS[k])
			continue
		if not SERVERS[k] is None:
			server = SERVERS[k]
			if VERBOSE:
				print "%3d: %s"%(k,server.__str__())
			for i in ["game_date","start_date","companies_max","companies_on","spectators_max","use_password","clients_max","clients_on","spectators_on","dedicated"]:
				if not i in counters.keys():
					counters[i] = 0
				counters[i] += getattr(server, i)
			
			# handle list fields
			for i in ["server_revision","server_lang","map_name","map_width","map_set"]:
				key = getattr(server, i)
				if i == "map_height":
					key = "%5d x %-5d" % (server.map_width, server.map_height)
				if not key in counters[i].keys():
					# 0 = counter
					# 1 = client counter
					counters[i][key] = [0, 0]
				counters[i][key][0] += 1
				counters[i][key][1] += server.clients_on
			
			if server.server_name.find("myottd.net") >= 0:
				myottdservers += 1
				
			# grf stats
			grfs = SERVERS[k].grfs
			for grf in grfs:
				grfname = grf[1]
				if not grfname in total_grfs:
					total_grfs[grfname] = Grf(grf[0], grf[1])
				if not grfname in used_grfs.keys():
					used_grfs[grfname] = 0
					grfclients[grfname] = 0
				used_grfs[grfname] += 1
				grfclients[grfname] += server.clients_on
				total_grfs[grfname].addServer(server)
				grfcount += 1
			
			if len(grfs) > 0:
				valid = True
				if len(grfs) == 1:
					if grfs[0][0].encode('hex') == '52570103': #ignore generic tram GRF
						valid = False
				if valid:
					newgrf_servers += 1
					newgrf_clients += server.clients_on
			clients_overall += server.clients_on
			sumcounter+=1
	if VERBOSE:
		print '#'*80
	print "OpenTTD Server statistics (%s):" % time.ctime()
	print "companies: %d / %d" % (counters["companies_on"], counters["companies_max"])
	print "spectators: %d / %d" % (counters["spectators_on"], counters["spectators_max"])
	print "clients: %d / %d" % (counters["clients_on"], counters["clients_max"])
	print "password protected servers: %d" % counters["use_password"]
	print "dedicated servers: %d / %d, %.2f %%" % (counters["dedicated"], sumcounter, (float(counters["dedicated"])/float(sumcounter))*100)
	print "newGRF servers: %d / %d (%.2f%%)" % (newgrf_servers, sumcounter, (float(newgrf_servers)/float(sumcounter))*100)
	print "players on newGRF servers: %d / %d (%.2f%%)" % (newgrf_clients, clients_overall, (float(newgrf_clients)/float(clients_overall))*100)
	print "responding servers: %d, not responding: %d" % (len(SERVERS.keys()) - servererr, servererr)
	print "myottd.net servers online: %d" % (myottdservers)
	
	
	print ""
	print "used versions:"
	for item in sorted(counters["server_revision"].items(), key=itemgetter(1), reverse=True):
		print " % 16s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
	
	print ""
	print "used map sizes:"
	for item in sorted(counters["map_width"].items(), key=itemgetter(1), reverse=True):
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
		
	print ""
	print "used languages:"
	for item in sorted(counters["server_lang"].items(), key=itemgetter(1), reverse=True):
		if item[0] <= len(known_languages):
			langstr = known_languages[item[0]]
		else:
			langstr = "unkown language: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (langstr, item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
	
	print ""
	print "used landscapes:"
	landscapes = ['normal', 'arctic', 'tropic', 'toyland']
	for item in  sorted(counters["map_set"].items(), key=itemgetter(1), reverse=True):
		if item[0] < 4:
			lcs = landscapes[item[0]]
		else:
			lcs = "unkown landscape: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (lcs, item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
		
	print ""
	print "used maps:"
	for item in sorted(counters["map_name"].items(), key=itemgetter(1), reverse=True):
		print " % 50s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])

	print ""
	print "used GRFs (%d used, %d unique known):" % (grfcount, len(total_grfs))
	for item in sorted(total_grfs.values(), reverse=True):
		print item.__str__(grfcount)
	sys.exit(0)

if __name__ == '__main__':
	main()
