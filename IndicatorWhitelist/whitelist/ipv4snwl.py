from .whitelist import Whitelist
from netaddr import IPNetwork,IPSet
from .master import IndicatorTypes

class IPv4SubnetWL(Whitelist):
    """IPv4 Subnet whitelist.
    This class stores its whitelisted IPv4 subnets in the ipv4sn table.
    This stores the CIDR and the max and min ip specified by the CIDR.
    """
    @staticmethod
    def getCreateTable():
        """Create the table to hold the subnet information"""
        return "create table ipv4sn (cidr char(20), minip integer(11), maxip integer(11) )"

    @staticmethod
    def storeDB(conn,subnets):
        """Overwrite the subnet info in the table with the specified subnets (string) in the database."""
        c=conn.cursor()
        vals=[]
        for sn in subnets:
            cidr=IPNetwork(sn);
            vals.append( (str(cidr),cidr.first,cidr.last))
        c.execute("delete from ipv4sn")
        c.executemany("insert into ipv4sn(cidr,minip,maxip) values (?,?,?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        If the indicator is a single address, it is whitelisted if it is included in any CIDR.
        If the indicator is a network spec, it is whitelisted if all of the addresses it represents are included in any CIDR
        """
        sn=IPNetwork(indicator)
        minip=sn.first
        maxip=sn.last

        c=conn.cursor()
        c.execute("select cidr,minip,maxip from ipv4sn where ? between minip and maxip or ? between minip and maxip order by minip",(minip,maxip))
        ipset=None
        rec=c.fetchone()
        # create a set of all ips contained network specs that contain the min and max ip specified by the indicator
        while (rec != None):
            if(ipset==None):
                ipset = IPSet(IPNetwork(rec[0]))
            else:
                ipset = ipset | IPSet(IPNetwork(rec[0]))
            rec=c.fetchone()
        # if the resulting set is empty, the indicator is not whitelisted
        if(ipset == None):
            return False
        # if the set of IPs represented by the indicator is a subset of the IPs set created above, then it is whitelisted
        ips=IPSet(sn)
        if(ips.issubset(ipset)):
            rv=True
        else:
            rv=False
        c.close()
        return rv
