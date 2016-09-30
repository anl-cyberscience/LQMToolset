from .whitelist import Whitelist


class IPv6WL(Whitelist):
    """
    IPv6 address whitelist.
    This class stores its whitelisted IPv6 address in the ipv4addr table.
    """

    @staticmethod
    def getCreateTable():
        return "create table ipv6addr (addr char(40))"

    @staticmethod
    def storeDB(conn, ipv6addrs):
        """Overwrite the addresses in the table with the specified addresses (string) in the database."""
        connection = conn.cursor()
        vals = []
        for ipv6addr in ipv6addrs:
            vals.append((ipv6addr,))
        connection.execute("delete from ipv6addr")
        connection.executemany("insert into ipv6addr(addr) values (?)", iter(vals))
        connection.close()

    def isWhitelisted(self, conn, indicatorType, indicator):
        """
        Return whether or not the indicator of type indicatorType is whitelisted by this whitelist.
        This checks the indicator against the addresses in the table and requires an exact match to be considered
        whitelisted.
        """
        connection = conn.cursor()
        connection.execute("select addr from ipv6addr where addr=?", (indicator,))
        rec = connection.fetchone()
        connection.close
        return rec is not None
