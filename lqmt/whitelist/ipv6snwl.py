from .whitelist import Whitelist
from netaddr import IPNetwork,IPSet

class IPv6SubnetWL(Whitelist):
    """IPv6 Subnet whitelist.
    This class is not yet implemented
    """

    @staticmethod
    def getCreateTable():
        return "create table ipv6sn (cidr char(40), minip integer(60), maxip integer(60) )"

    @staticmethod
    def storeDB(conn,subnets):
        """Overwrite the subnet info in the table with the specified subnets (string) in the database."""
        c = conn.cursor()
        vals = []
        for sn in subnets:
            cidr = IPNetwork(sn);
            vals.append((str(cidr), cidr.first, cidr.last))
        c.execute("delete from ipv6sn")
        c.executemany("insert into ipv6sn(cidr,minip,maxip) values (?,?,?)", iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        raise NotImplementedError
