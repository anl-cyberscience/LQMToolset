"""
Created on Jan 12, 2015

@author: taxon
"""
import FlexTransform
from lqmt.lqm.data import Alert
import os
import inspect
import logging
import io


class FlexTransformParser(object):
    def __init__(self, config):
        self._logger = logging.getLogger("LQMT.Parsers")

        # get the FlexTransform directory
        self._current_dir, name = os.path.split(inspect.getfile(FlexTransform.FlexTransform))
        self._transform = FlexTransform.FlexTransform.FlexTransform()

        # con
        for p, c in config.items():
            self.addParser(p, c)

    def addParser(self, parserName, parserConfiguration):
        """
        Function that extends the AddParser function from FlexTransform.
        :param parserName: Name of the parser being added
        :param parserConfiguration: Path to the configuration file being added
        """
        if parserName not in self._transform.Parsers:
            config_file = open(os.path.join(self._current_dir, parserConfiguration), 'r')
            self._transform.AddParser(parserName, config_file)

    def parse(self, datafile, meta):
        """
        Parse the datafile using the metadata dictionary.

        Note: Removed sourceMetaData from the parser for now due to conflicts with STIX-TLP. Currently assessing
        if it needs to be included. Currently the meta file is just being used to identify the sourceParser.

        :param datafile: Contains path to the file containing the alert data.
        :param meta: Contains meta data about the datafile. Examples includes PayloadFormat, FileName, PayloadType, and
        more.
        :return: Returns parsed alert data.
        """
        alerts = []

        # TODO: Stix-tlp parser currently doesn't support meta files. Until it's support, we will only send meta file's
        # for non-stix payloads.
        try:
            if meta['PayloadFormat'] == 'stix-tlp':
                data = self._transform.TransformFile(sourceFileName=datafile, sourceParserName=meta['PayloadFormat'],
                                                     targetParserName='LQMTools')
            else:
                data = self._transform.TransformFile(sourceFileName=datafile, sourceParserName=meta['PayloadFormat'],
                                                     targetParserName='LQMTools', sourceMetaData=meta)
        except Exception as e:
            data = []
            self._logger.error(
                "LQMT-FlexTransform-Parser: Error parsing file file='{0}' exception='{1}'".format(datafile, e))

        for d in data:
            alert = Alert()
            alert.setFromDict(d)
            alerts.append(alert)

        return alerts

    def parseflextext(self, datafile, meta, destination_file_obj, config_str):
        """
        Flextext parser. Transforms intermediate data into a user defined structure.

        :param datafile: dir path to the alert datafile that will be transformed
        :param meta: Contains meta data about the datafile. Examples includes PayloadFormat, FileName, PayloadType, and
        more.
        :param destination_file_obj: File object used to write contents to file.
        :param config_str: Parser configuration in the form of a string. Is wrapped in an IO wrapped and then passed
        to FlexT to configure FlexText parser
        :return: Returns none. Data is outputted to file specified by destination_file_obj
        """

        # Add FlexText parser using config_str wrapped in StringIO object
        if 'FlexText' not in self._transform.Parsers:
            config_str_io = io.StringIO(config_str)
            config_str_txt = io.StringIO(config_str_io.read())
            self._transform.AddParser("FlexText", config_str_txt)

        # Run FlexText parser
        try:
            if meta['PayloadFormat'] == 'stix-tlp':
                self._transform.TransformFile(
                    sourceFileName=datafile,
                    targetFileName=destination_file_obj,
                    sourceParserName=meta['PayloadFormat'],
                    targetParserName="FlexText",
                )
            else:
                self._transform.TransformFile(
                    sourceFileName=datafile,
                    targetFileName=destination_file_obj,
                    sourceParserName=meta['PayloadFormat'],
                    targetParserName="FlexText",
                    sourceMetaData=meta
                )

        except Exception as e:
            self._logger.error(
                "LQMT-FlexText-Parser: Error parsing file file='{0}' exception='{1}'".format(datafile, e))
