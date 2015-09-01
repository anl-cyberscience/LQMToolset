from .whitelist import Whitelist

class IPv6WL(Whitelist):
    """IPv6 address whitelist.
    This class is not yet implemented
    """

    @staticmethod
    def getCreateTable():
        return "create table ipv6addr (addr char(40))"

    @staticmethod
    def storeDB(conn,ipv6addrs):
        c=conn.cursor()
        vals=[]
        for ipv6addr in ipv6addrs:
            vals.append( (ipv6addr,) )
        c.execute("delete from ipv6addr")
        c.executemany("insert into ipv6addr(addr) values (?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        raise NotImplementedError
