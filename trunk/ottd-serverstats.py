#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *
VERBOSE = False
SERVERS = {}

class ClientGameInfo(Client):
	# this class implements the thread start method
	def run(self):
		self.connect()
		if len(self.errors) == 0:
			SERVERS[self.uid] = self.getGameInfo()
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
	counters[6] = {} # server revision
	counters[7] = {} # language
	counters[12] = {} # map
	counters[13] = {} # map-size
	counters[15] = {} # landscape
	used_grfs = {}
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
			server = SERVERS[k][0]
			if VERBOSE:
				print "%3d: %s"%(k,server.__str__())
			for i in [0,1,2,3,4,8,9,10,11,16]:
				if not i in counters.keys():
					counters[i] = 0
				counters[i] += server[i]
			
			# handle list fields
			for i in [6,7,12,13,15]:
				key = server[i]
				if i == 13:
					key = "%5d x %-5d" % (server[13], server[14])
				if not key in counters[i].keys():
					# 0 = counter
					# 1 = client counter
					counters[i][key] = [0, 0]
				counters[i][key][0] += 1
				counters[i][key][1] += server[10]
			
			if server[5].find("myottd.net") >= 0:
				myottdservers += 1
				
			# grf stats
			grfs = SERVERS[k][1]
			for grf in grfs:
				grfname = grf[0]
				if not grfname in used_grfs.keys():
					used_grfs[grfname] = 0
					grfclients[grfname] = 0
				used_grfs[grfname] += 1
				grfclients[grfname] += server[10]
				grfcount += 1
			
			if len(grfs) > 0:
				valid = True
				if len(grfs) == 1:
					if grfs[0][0].encode('hex') == '52570103': #ignore generic tram GRF
						valid = False
				if valid:
					newgrf_servers += 1
					newgrf_clients += server[10]
			clients_overall += server[10]
			sumcounter+=1
	#0 game_date
	#1 start_date
	#2 companies_max
	#3 companies_on
	#4 spectators_max
	#5 server_name
	#6 server_revision
	#7 server_lang
	#8 use_password
	#9 clients_max
	#10 clients_on
	#11 spectators_on
	#12 map_name
	#13 map_width
	#14 map_height
	#15 map_set
	#16 dedicated
	if VERBOSE:
		print '#'*80
	print "OpenTTD Server statistics (%s):" % time.ctime()
	print "companies: %d / %d" % (counters[3], counters[2])
	print "spectators: %d / %d" % (counters[11], counters[4])
	print "clients: %d / %d" % (counters[10], counters[9])
	print "password protected servers: %d" % counters[8]
	print "dedicated servers: %d / %d, %.2f %%" % (counters[16], sumcounter, (float(counters[16])/float(sumcounter))*100)
	print "newGRF servers: %d / %d (%.2f%%)" % (newgrf_servers, sumcounter, (float(newgrf_servers)/float(sumcounter))*100)
	print "players on newGRF servers: %d / %d (%.2f%%)" % (newgrf_clients, clients_overall, (float(newgrf_clients)/float(clients_overall))*100)
	print "responding servers: %d, not responding: %d" % (len(SERVERS.keys()) - servererr, servererr)
	print "myottd.net servers online: %d" % (myottdservers)
	
	
	print ""
	print "used versions:"
	for item in sorted(counters[6].items(), key=itemgetter(1), reverse=True):
		print " % 16s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
	
	print ""
	print "used map sizes:"
	for item in sorted(counters[13].items(), key=itemgetter(1), reverse=True):
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
		
	print ""
	print "used languages:"
	for item in sorted(counters[7].items(), key=itemgetter(1), reverse=True):
		if item[0] <= len(known_languages):
			langstr = known_languages[item[0]]
		else:
			langstr = "unkown language: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (langstr, item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
	
	print ""
	print "used landscapes:"
	landscapes = ['normal', 'arctic', 'tropic', 'toyland']
	for item in  sorted(counters[15].items(), key=itemgetter(1), reverse=True):
		if item[0] < 4:
			lcs = landscapes[item[0]]
		else:
			lcs = "unkown landscape: %d" % item[0]
		print " % 20s: %3d (% 5.1f%%), %3d clients" % (lcs, item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])
		
	print ""
	print "used maps:"
	for item in sorted(counters[12].items(), key=itemgetter(1), reverse=True):
		print " % 50s: %3d (% 5.1f%%), %3d clients" % (item[0], item[1][0], (float(item[1][0])/float(sumcounter))*100, item[1][1])

	print ""
	print "used GRFs (%d used, %d unique known):" % (grfcount, len(used_grfs))
	for item in sorted(used_grfs.items(), key=itemgetter(1), reverse=True):
		print " % 10s: %3d (% 5.1f%%), %3d clients" % (item[0].encode('hex'), item[1], (float(item[1])/float(grfcount))*100, grfclients[item[0]])
	
	sys.exit(0)

if __name__ == '__main__':
	main()