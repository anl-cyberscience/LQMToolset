from .whitelist import Whitelist

class DomainWL(Whitelist):
    """Domain whitelist.
    This class stores its whitelisted domains in the domian table.  If a domain is in the table it is whitelisted.
    """

    @staticmethod
    def getCreateTable():
        """Create the table to hold the domains"""
        return "create table domain (domain char(256))"

    @staticmethod
    def storeDB(conn,domains):
        """Overwrite the domains in the table with the specified domains (string) in the database."""
        c=conn.cursor()
        vals=[]
        for domain in domains:
            vals.append( (domain,) )
        c.execute("delete from domain")
        c.executemany("insert into domain(domain) values (?)",iter(vals))
        c.close()

    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        This will check for all subdomains as well."""
        c=conn.cursor()
        # sqlite: || is concatenation
        c.execute("select domain from domain where ? like '%' || domain",(("%"+indicator),))
        rec=c.fetchone()
        c.close()
        return rec != None
