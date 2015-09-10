from .whitelist import Whitelist

class HostWL(Whitelist):
    """Domain whitelist.
    This class stores its whitelisted hosts in the host table.  If a host is in the table it is whitelisted.
    """
    @staticmethod
    def getCreateTable():
        """Create the table to hold the hostnames"""
        return "create table host (host char(256))"

    @staticmethod
    def storeDB(conn,hosts):
        """Overwrite the hosts in the table with the specified hosts (string) in the database."""
        c=conn.cursor()
        vals=[]
        for host in hosts:
            vals.append( (host,) )
        c.execute("delete from host")
        c.executemany("insert into host(host) values (?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        This checks the indicator against the hosts in the table and requires an exact match to be considered whitelisted."""
        c=conn.cursor()
        c.execute("select host from host where host=?",(indicator,))
        rec=c.fetchone()
        c.close()
        return rec != None

        