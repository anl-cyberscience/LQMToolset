'''
Created on Jan 12, 2015

@author: taxon
'''
from FlexTransform import FlexTransform
from lqmt.lqm.data import Alert
import os
import inspect
import logging

class FlexTransformParser(object):

    def __init__(self,config):
        self._logger = logging.getLogger("LQMT.Parsers")
        # get the FlexTransform directory
        currentdir,name = os.path.split(inspect.getfile(FlexTransform))
        self._transform=FlexTransform.FlexTransform()
        #configItems contains a list of key,value pairs key=Parser/Format name, value=FX config file
        for p,c in config.items():
            f=open(os.path.join(currentdir,c), 'r')
            # add the parser info to the FX instance
            self._transform.AddParser(p, f)

    def parse(self, datafile, meta):
        """Parse the datafile using the metadatra dictionary."""
        alerts=[]
        try:
            data = self._transform.TransformFile(sourceFileName=datafile, sourceParserName=meta['PayloadFormat'], targetParserName='LQMTools', sourceMetaData=meta)
        except Exception as e:
            data=[]
            self._logger.error("CFM: Error parsing file file='{0}' exception='{1}'".format(datafile,e) )

        for d in data:
            alert=Alert()
            alert.setFromDict(d)
            alerts.append(alert)
        return alerts



