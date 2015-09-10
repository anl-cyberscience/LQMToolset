from .whitelist import Whitelist

class URLWL(Whitelist):
    """IPv4 address whitelist.
    This class stores its whitelisted URLs  in the url table.
    """

    @staticmethod
    def getCreateTable():
        """Create the table to hold the URLs"""
        return "create table url (url char(256))"

    @staticmethod
    def storeDB(conn,urls):
        """Overwrite the URLs in the table with the specified URLs (string) in the database."""
        c=conn.cursor()
        vals=[]
        for url in urls:
            vals.append( (url,) )
        c.execute("delete from url")
        c.executemany("insert into url(url) values (?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        This checks the indicator against the URLs in the table and requires an exact match to be considered whitelisted."""
        c=conn.cursor()
        c.execute("select url from url where url=?",(indicator,))
        rec=c.fetchone()
        c.close()
        return rec != None
