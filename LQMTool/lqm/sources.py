class Source(object):
    """The superclass for all sources"""
    
    def getFilesToProcess(self):
        """Return an iterator that will return alert/metadta file tuples"""
        NotImplementedError

    def processed(self,datafile):
        """A file pair has been processed"""
        NotImplementedError
        
    def logStatistics(self, numAlerts):
        """Print any statistics to loggers.  This is called when the source has been completely traversed"""
        NotImplementedError