#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *

def printUsage():
	print "usage: %s <ip:port>" % sys.argv[0]
	sys.exit(1)

def main():
	if len(sys.argv) == 0:
		printUsage()
	
	try:
		ip, port = sys.argv[1].split(':')
		port = int(port)
	except:
		printUsage()

	client = Client(ip, port)
	client.connect(M_UDP)
	print "getting game info ..."
	gi=client.getGameInfo()
	if not gi is None:
		for k in ["companies_max","companies_on", "spectators_max", "server_name", "server_revision", "server_lang", "use_password", "clients_max", "clients_on", "spectators_on", "map_name", "map_width", "map_height", "map_set", "dedicated"]:
			print "%20s: %s" % (k, getattr(gi, k))
	
	print ""
	print "getting company info ..."
	cis=client.getCompanyInfo()
	if not cis is None:
		for ci in cis:
			print "\n === company %d"%(ci.number)
			for k in ["company_name", "inaugurated_year", "company_value", "money", "income", "performance", "password_protected"]:
				print "%20s: %s"%(k, getattr(ci, k))
	
	print ""
	print "getting grf info ..."
	if len(gi.grfs) > 0:
		grfs=client.getGRFInfo(gi.grfs)
		if not grfs is None:
			for grf in grfs:
				print " %40s - %s - %s" % (grf[2], grf[0].encode("hex"), grf[1].encode("hex"))
	else:
		print " no grfs used"
	
	client.disconnect()

if __name__ == '__main__':
	main()
