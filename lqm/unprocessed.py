import os

class UnprocessedAlertHandler(object):
    """Object to handle unprocessed alerts."""

    def __init__(self, csvTool):
        self._toCSV=csvTool
    
    def initialize(self):
        self._toCSV.initialize()
        
    def unprocessed(self,alert):
        self._toCSV.process(alert)
