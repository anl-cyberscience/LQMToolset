"""
Created on March 29, 2018

@author: grjohnson
"""
import os
import logging
import toml
from lqmt.lqm.data import RuleFile


class RuleParser(object):
    def __init__(self, config=None):
        """
        :param config: configuration file
        """
        # currently no config parameters
        self._logger = logging.getLogger("LQMT.Parsers")

        # accepted configuration values
        self._accepted_rules = ['snort', 'yara']

        # default lists
        self._sources = []
        self._rules = []
        self._line_offset = 0  # allows for non-snort compliant header that can be removed

        if config is not None:
            # parse config files
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

                if 'rules' in topconfig['Filters'][0]:
                    temp = topconfig['Filters'][0]['rules']
                    for x in temp:
                        if x.lower() in self._accepted_rules:
                            self._rules.append(x.lower())
                        else:
                            self._logger.warning("Incompatible rule for parser " + x)

                if 'start_offset' in topconfig['Filters'][0]:
                    self._line_offset = topconfig['Filters'][0]['start_offset']


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

    def __check_filetype(self, meta):
        ret = 'unknown'

        if 'PayloadFormat' in meta:
            l = meta['PayloadFormat']
            if l == 'SnortRules':
                ret = 'snort'
            elif l == 'YaraRules':
                ret = 'yara'

        return ret

    def custom_parser(self, datafile):
        ret = []

        return ret

    def parse(self, datafile, meta=None):
        alerts = []
        source_match = True
        rule_type = 'unknown'
        rules_dict = {'snort': [], 'yara': []}

        try:
            alert = RuleFile()

            if meta:
                # filter by sources
                source_match = self.__check_meta(meta)
                # determine the file format - snort versus yara
                rule_type = self.__check_filetype(meta)

            if source_match:
                if os.path.exists(datafile):
                    with open(datafile, 'r') as file:
                        data = file.read()
                        alert.setRawFile(data)

                if rule_type == 'snort' and 'snort' in self._rules:
                    with open(datafile, 'r') as file:
                        data_l = file.readlines()

                    # seek to start line (array of start line by sources?)
                    rules_dict['snort'] = data_l[self._line_offset:]
                    alert.setRules(rules_dict)
                elif rule_type == 'yara' and 'yara' in self._rules:
                    rules_dict['yara'].append(data)
                    alert.setRules(rules_dict)
                else:
                    self._logger.warning(
                        "LQMT-Rule-Parser: Unrecognized or unconfigured rule type={0}".format(rule_type))

                alerts.append(alert)
        except Exception as e:
            self._logger.error("LQMT-Rule-Parser: Problem with parsed data. Exception={0}".format(e))

        return alerts
