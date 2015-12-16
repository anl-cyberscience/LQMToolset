"""
Created on Jan 12, 2015

@author: taxon
"""
import FlexTransform
from lqmt.lqm.data import Alert
import os
import inspect
import logging


class FlexTransformParser(object):
    def __init__(self, config):
        self._logger = logging.getLogger("LQMT.Parsers")

        # get the FlexTransform directory
        currentdir, name = os.path.split(inspect.getfile(FlexTransform.FlexTransform))
        self._transform = FlexTransform.FlexTransform.FlexTransform()

        # configItems contains a list of key,value pairs key=Parser/Format name, value=FX config file
        for p, c in config.items():
            f = open(os.path.join(currentdir, c), 'r')

            # add the parser info to the FX instance
            self._transform.AddParser(p, f)

    def parse(self, datafile, meta):
        """
        Parse the datafile using the metadata dictionary.

        :param datafile: Contains path to the file containing the alert data.
        :param meta: Contains meta data about the datafile. Examples includes PayloadFormat, FileName, PayloadType, and
        more.
        :return: Returns parsed alert data.
        """
        alerts = []
        try:
            data = self._transform.TransformFile(sourceFileName=datafile, sourceParserName=meta['PayloadFormat'],
                                                 targetParserName='LQMTools', sourceMetaData=meta)
        except Exception as e:
            data = []
            self._logger.error("CFM: Error parsing file file='{0}' exception='{1}'".format(datafile, e))

        for d in data:
            alert = Alert()
            alert.setFromDict(d)
            alerts.append(alert)

        return alerts

    def parseflextext(self, datafile, destination):
        """
        Flextext parser. Transforms intermediate data into a user defined structure.

        :param datafile: dir path to the alert datafile that will be transformed
        :param destination: dir path to where the transformed data should be placed. The destination var is turned into
        file object before being passed to FlexT.
        :return: Returns none. Data is outputted to file specified by destination variable.
        """

        try:
            with open(destination, "w") as destination_file_obj:
                self._transform.TransformFile(
                    sourceFileName=datafile,
                    targetFileName=destination_file_obj,
                    sourceParserName='Cfm13Alert',
                    targetParserName="CSV"
                )

        except Exception as e:
            self._logger.error("CFM: Error parsing file file='{0}' exception='{1}'".format(datafile, e))
