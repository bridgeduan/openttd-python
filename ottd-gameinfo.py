#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
from ottd_lib import *
from ottd_grfs import GrfDB

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
    if gi.clients_on < gi.clients_max:
        # try connecting using TCP
        try:
            client.connect(M_TCP)
            cis = client.getTCPCompanyInfo()
            using_tcp = True
        except:
            cis = client.getCompanyInfo()
            using_tcp = False
    else:
        cis=client.getCompanyInfo()
        using_tcp = False
    if not cis is None:
        for ci in cis:
            print "\n === company %d"%(ci.number)
            for k in ["company_name", "inaugurated_year", "company_value", "money", "income", "performance", "password_protected"]:
                print "%20s: %s"%(k, getattr(ci, k))
            if using_tcp:
                print "%20s: %s"%("Clients", ci.players)
            elif hasattr(ci, "clients"):
                print "%20s:"%("Clients")
                for cli in ci.clients:
                    print "%30s" % cli.client_name
                
    
    print ""
    print "getting grf info ..."
    gi.newgrfs = []
    if len(gi.grfs) > 0:
        grfdatabase = GrfDB()
        grfdatabase.loadfromfile("newgrfs.grflist")
        unknowngrfs = grfdatabase.getgrfsnotinlist(gi.grfs)
        if len(unknowngrfs) > 0:
            unknowngrfs=client.getGRFInfo(gi.unknowngrfs)
        for grf in gi.grfs:
            if not grfdatabase.hasgrf(grf[1]) and not unknowngrfs is None:
                grfdatabase.addgrfinlist(unknowngrfs, grf[0])
            gi.newgrfs.append((grf[0], grf[1], grfdatabase.getgrfname(grf)))
        grfdatabase.savetofile("newgrfs.grflist")
        for grf in gi.newgrfs:
            print " %40s - %s - %s" % (grf[2], grf[0].encode("hex"), grf[1].encode("hex"))
    else:
        print " no grfs used"
    
    client.disconnect()

if __name__ == '__main__':
    main()
