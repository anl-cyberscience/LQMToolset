"""
Created on March 13, 2018

@author: grjohnson
"""
import os
import logging
import toml
import ramrod
import jsonpath_rw
from stix.core import STIXPackage
from stix.common import information_source
from lqmt.lqm.data import StixFile


class STIXParser(object):
    def __init__(self, config=None):
        """
        Class for parsing STIX files.  Allows a user to do the following:
        - Filter files based on the information source
        - Pass the full raw file to a tool
        - Parse requested STIX elements into a dictionary object for a tool.
        - Parse COA rules (snort and yara) into full context and specific rule dictionaries for a tool.

        :param config: configuration file
        """
        # currently no config parameters
        self._logger = logging.getLogger("LQMT.Parsers")

        # accepted configuration values
        self._accepted_elements = ['stix_header', 'observables', 'indicators', 'ttps', 'exploit_targets', 'incidents',
                                   'courses_of_action', 'campaigns', 'threat_actors', 'related_packages']
        self._accepted_rules = ['snort', 'yara']

        # default some lists
        self._sources = []
        self._elements = []
        self._rules = []

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

                if 'elements' in topconfig['Filters'][0]:
                    temp = topconfig['Filters'][0]['elements']
                    for x in temp:
                        if x.lower() in self._accepted_elements:
                            self._elements.append(x.lower())
                        else:
                            self._logger.warning("Incompatible STIX element configured " + x)

                if 'rules' in topconfig['Filters'][0]:
                    temp = topconfig['Filters'][0]['rules']
                    for x in temp:
                        if x.lower() in self._accepted_rules:
                            self._rules.append(x.lower())
                        else:
                            self._logger.warning("Incompatible rule for parser " + x)

    def __check_meta(self, meta):
        """
        Parses the Meta Data file looking for originators and custodians that match the user requested information source.

        :param meta: Meta data envelope for the file to be parsed
        :return Boolean: True if match is found, otherwise False.
        """
        ret = False

        # If there is no entry returns false for finding a match
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

    def __check_info_source(self, datafile):
        """
        Parses the STIX Header element looking for an Information source element matching the configured value.
        Currently only matches to STIX Header, long-term could check every Information Source element.

        :param datafile: The file sent to be parsed, expected to be STIX XML format.
        :return Boolean: True if match is found, otherwise False.
        """
        ret = False

        try:
            # TODO: Parse only header or look for all Information_Source elements?
            # attempt to map as a STIX Package, if fails force an update with ramrod
            try:
                stix_package = STIXPackage.from_xml(datafile)
            except Exception as e:
                self._logger.warning("Unable to parse XML to STIX, attempting version change Exception={0}".format(e))
                updated = ramrod.update(datafile, force=True)
                stix_package = STIXPackage.from_xml(updated)

            # Compare the information source from the stix_header
            info_src = stix_package.stix_header.information_source
            if info_src.identity:
                if info_src.identity.name in self._sources:
                    return True

            # If there are contributing sources, parse and compare to source list
            if info_src.contributing_sources:
                if info_src.contributing_sources._inner_name == 'sources':
                    for x in info_src.contributing_sources._inner:
                        if type(x) is information_source.InformationSource:
                            if x.identity.name in self._sources:
                                return True
        except Exception as e:
            self._logger.warning(
                "Unable to force XML to STIX with ramrod. Unable to check source Exception={0}".format(e))
            return ret

        if ret is False:
            self._logger.info("Did not identify the requested source in STIX Header.")

        return ret

    def custom_parser(self, datafile):
        """
        Custom parser for the XML STIX file.
        Successful parsing results in a STIX File object for a tool containing the raw file, requested elements,
        and rule signatures found.

        :param datafile: The file sent to be parsed, expected to be STIX XML format.
        :return alert: A Stix File object containing the parsed elements for tools
        """
        ret = []
        rule_list = []
        el_list = []

        try:
            alert = StixFile()

            # open to set the raw file text in the alert object
            if os.path.exists(datafile):
                with open(datafile, 'r') as file:
                    data = file.read()
                    alert.setRawFile(data)

            try:
                # attempt to map as a STIX Package, if fails force an update with ramrod
                stix_package = STIXPackage.from_xml(datafile)
            except Exception as e:
                self._logger.warning("Unable to parse XML to STIX, attempting version change Exception={0}".format(e))
                updated = ramrod.update(datafile, force=True)
                stix_package = STIXPackage.from_xml(updated)

            stix_dict = stix_package.to_dict()

            # parse as a STIX package to find matching elements
            if self._elements:
                for i in self._elements:
                    test = jsonpath_rw.parse('$.' + str(i).lower())  # returns all JSON key matches
                    for match in test.find(stix_dict):
                        el_list.append(match.value)
                alert.setStixElements(el_list)

            # create dictionary with a key for each entry in rules list
            rules_dict = {}
            for y in self._rules:
                rules_dict[y] = []

            # parse the STIX package to find elements containing Rules
            if self._rules:
                # search STIX for all test mechanisms
                test = jsonpath_rw.parse('$..test_mechanisms')  # STIX defined element that contains rules
                for match in test.find(stix_dict):
                    rule_list.append(match.value[0])
                    # compare the XSI type to see if it's in the rules list 'xsi:type' = 'yaraTM:YaraTestMechanismType'
                    for y in self._rules:
                        if y.lower() in str(match.value[0]['xsi:type']).lower():  # STIX way to determine rule type
                            # append to list of rules for dictionary entry for "rule[s]" -- 'rule[s]' -> 'value'
                            if 'rule' in match.value[0]:
                                rules_dict[y].append(match.value[0]['rule']['value'])
                            elif 'rules' in match.value[0]:
                                for z in match.value[0]['rules']:
                                    rules_dict[y].append(z['value'])  # TODO: remove hardcoding
                # TODO: STIX Snort Specification allows -- Event Filters / Rate Filters / Event Suppression
                alert.setRules(rules_dict)
                alert.setFullRules(rule_list)

            # append the final alert
            ret.append(alert)

            self._logger.info("Identified {0} matching elements and {1} rule objects.".format(len(el_list), len(rule_list)))
        except Exception as e:
            self._logger.error("Error occurred parsing STIX file. Exception={0}".format(e))
            return ret

        return ret

    def parse(self, datafile, meta=None):
        """
        Parses a STIX File to return the raw file, requested elements, and rule signatures found.

        :param datafile: The STIX XML file to be parsed.
        :param meta: The meta data envelope for the STIX XML file to be parsed
        :return alerts: A list of STIX File objects parsed from the STIX XML file.
        """
        alerts = []
        source_match = False
        parse_data = False

        # Create the object file to pass to the tool chains
        try:
            self._logger.warning("Beginning to parse " + datafile)

            # if filtering by STIX information source
            if self._sources:
                # check both in the XML and in the meta data
                if meta:
                    if self.__check_meta(meta):
                        source_match = True
                    else:
                        source_match = self.__check_info_source(datafile)
                else:
                    source_match = self.__check_info_source(datafile)
            else:  # if no filters set then pass
                source_match = True

            # check for filter matches
            if source_match:
                parse_data = True
            else:
                self._logger.warning("Did not find match the requested source as the datafile producer.")

            if parse_data:
                alerts = self.custom_parser(datafile)

        except Exception as e:
            self._logger.error("LQMT-STIX-Parser: Problem with parsed data. Exception={0}".format(e))

        return alerts
