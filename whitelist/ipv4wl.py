from .whitelist import Whitelist

class IPv4WL(Whitelist):
    """IPv4 address whitelist.
    This class stores its whitelisted IPv4 address in the ipv4addr table.
    """
    @staticmethod
    def getCreateTable():
        """Create the table to hold the addresses"""
        return "create table ipv4addr (addr char(15))"

    @staticmethod
    def storeDB(conn,ipv4addrs):
        """Overwrite the addresses in the table with the specified addresses (string) in the database."""
        c=conn.cursor()
        vals=[]
        for ipv4addr in ipv4addrs:
            vals.append( (ipv4addr,) )
        c.execute("delete from ipv4addr")
        c.executemany("insert into ipv4addr(addr) values (?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        This checks the indicator against the addresses in the table and requires an exact match to be considered whitelisted."""
        c=conn.cursor()
        c.execute("select addr from ipv4addr where addr=?",(indicator,))
        rec=c.fetchone()
        c.close()
        return rec != None
