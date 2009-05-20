#!/bin/env python
# made by thomas {AT} thomasfischer {DOT} biz
from openttd.client import Client, M_UDP, M_TCP
from openttd.grfdb import GrfDB
import openttd.date
import sys

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
        print "%20s: %s" % ("game_date", str(openttd.date.OpenTTDDate(ottddate=gi.game_date).toDate()))
        print "%20s: %s" % ("start_date", str(openttd.date.OpenTTDDate(ottddate=gi.start_date).toDate()))
    else:
        return
    if gi.companies_on > 0:
        print ""
        print "getting company info ..."
        if gi.clients_on < gi.clients_max:
            # try connecting using TCP
            try:
                client.connect(M_TCP)
                cis = client.getTCPCompanyInfo()
                using_tcp = True
            except Exception, e:
                print "exception when connecting using tcp, trying udp: %s" % e
                cisi = client.getCompanyInfo()
                cis = cisi.companies
                using_tcp = False
        else:
            cisi=client.getCompanyInfo()
            cis = cisi.companies
            using_tcp = False
        if not cis is None:
            for ci in cis:
                print "\n === company %d"%(ci.number)
                for k in ["company_name", "inaugurated_year", "company_value", "money", "income", "performance", "password_protected"]:
                    print "%20s: %s"%(k, getattr(ci, k))
                if using_tcp:
                    print "%20s: %s"%("Clients", ci.clients)
                elif cisi.info_version < 5:
                    print "%20s:"%("Clients")
                    for cli in ci.clients:
                        if cli.join_date > 0:
                            jd = openttd.date.OpenTTDDate(ottddate=cli.join_date).toYMD()
                        else:
                            jd = [0,0,0]
                        print "%30s, joined %d - %d - %d" % (cli.client_name, jd[2], jd[1], jd[0])
                    
            if not using_tcp and cisi.info_version < 5 and len(cisi.spectators) > 0:
                print "\n === spectators"
                print "%20s:" % "Clients"
                for cli in cisi.spectators:
                    jd = client.dateToYMD(cli.join_date)
                    print "%30s, joined %d - %d - %d" % (cli.client_name, jd[2], jd[1], jd[0])
        else:
            return
    
    if len(gi.grfs) > 0:
        print ""
        print "getting grf info ..."
        gi.newgrfs = []
        grfdatabase = GrfDB()
        grfdatabase.loadfromfile("newgrfs.grflist")
        unknowngrfs = grfdatabase.getgrfsnotinlist(gi.grfs)
        if len(unknowngrfs) > 0:
            unknowngrfs=client.getGRFInfo(unknowngrfs)
        for grf in gi.grfs:
            if not grfdatabase.hasgrf(grf[1]) and not unknowngrfs is None:
                grfdatabase.addgrfinlist(unknowngrfs, grf[0])
            gi.newgrfs.append((grf[0], grf[1], grfdatabase.getgrfname(grf)))
        grfdatabase.savetofile("newgrfs.grflist")
        for grf in gi.newgrfs:
            print " %40s - %s - %s" % (grf[2], grf[0].encode("hex"), grf[1].encode("hex"))
    else:
        print ""
        print " no grfs used"
    
    client.disconnect()

if __name__ == '__main__':
    main()
