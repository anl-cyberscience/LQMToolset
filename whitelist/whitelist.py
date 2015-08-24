
class Whitelist(object):
    """
    Abstract superclass for all whitelist types
    """
    
    def isWhitelisted(self,conn,indicatorType,indicator):
        """Return whether or not the indicator of type indicatorType is whitelisted by this whitelist"""
        raise NotImplementedError