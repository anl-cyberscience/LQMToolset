"""
Created on July 26, 2018

@author: grjohnson
"""
import os
import logging
import toml
from lqmt.lqm.data import PdfFile


class PdfParser(object):
    def __init__(self, config=None):
        """
        :param config: configuration file
        """
        self._logger = logging.getLogger("LQMT.Parsers")
        self._sources = []

        if config is not None:
            for p, c in config.items():
                self.__parse_config(c)

    def __parse_config(self, configfile):
        """
        Extracts the defined configuration parameters for the parser.
        Important pre-condition is the user must configure elements and rules against a predefined enumeration.

        :param configfile: configuration file
        :return None:
        """
        if os.path.exists(configfile):
            cfg = open(configfile)
            topconfig = toml.loads(cfg.read())
            cfg.close()

            if 'Filters' in topconfig:
                if 'sources' in topconfig['Filters'][0]:
                    self._sources = topconfig['Filters'][0]['sources']

    def __check_meta(self, meta):
        """
        Parses the Meta Data file looking for originators and custodians that match the user requested information source.

        :param meta: Meta data envelope for the file to be parsed
        :return Boolean: True if match is found, otherwise False.
        """
        ret = False

        if not self._sources:
            return True

        # If there is no entry returns false for finding a match
        if 'SendingSite' in meta:
            l = meta['SendingSite']
            if l in self._sources:
                return True

        if 'DownloadElementExtendedAttribute' in meta:
            l = meta['DownloadElementExtendedAttribute']
            # this element can be either a list of dictionaries or a dictionary
            if type(l) is dict:
                if l['Field'] == 'Originator' or l['Field'] == 'Custodian':
                    if l['Value'] in self._sources:
                        return True
            elif type(l) is list:
                for x in l:
                    if x['Field'] == 'Originator' or x['Field'] == 'Custodian':
                        if x['Value'] in self._sources:
                            return True
            else:
                ret = False

        if ret is False:
            self._logger.info("Did not identify the requested source in meta-data file.")

        return ret

    def custom_parser(self, datafile):
        ret = []

        return ret

    def parse(self, datafile, meta=None):
        """
        Parser at this time just moves a binary file to the tool.  Implemented as a parser for future expansion.

        :param datafile: File to be processed
        :param meta: Meta data file for filters
        :return:
        """
        alerts = []
        source_match = True

        try:
            alert = PdfFile()

            if meta:
                # filter by sources
                source_match = self.__check_meta(meta)
                alert.setMeta(meta)

            if source_match:
                if os.path.exists(datafile):
                    with open(datafile, 'rb') as file:
                        data = file.read()
                        alert.setBinFile(data, filename=os.path.basename(file.name))

            alerts.append(alert)

        except Exception as e:
            self._logger.error("LQMT-PDF-Parser: Problem with parsed data. Exception={0}".format(e))

        return alerts
