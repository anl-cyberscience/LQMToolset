from .whitelist import Whitelist

class IPv6SubnetWL(Whitelist):
    """IPv6 Subnet whitelist.
    This class is not yet implemented
    """

    @staticmethod
    def getCreateTable():
        pass

    @staticmethod
    def storeDB(conn,subnets):
        raise NotImplementedError

    def isWhitelisted(self,conn,indicatorType,indicator):
        raise NotImplementedError
