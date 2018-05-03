"""
Created on March 29, 2018

@author: grjohnson
"""

import logging
import os
import pyshark
import arrow
import copy
import pyparsing as pyp
import itertools
from lqmt.lqm.tool import PullTool
from idstools import rule
from lqmt.lqm.exceptions import ConfigurationError
from zipfile import ZipFile


class FromSnort(PullTool):
    def __init__(self, config):
        """
        ToToolName description
        :param config: configuration file
        """
        super().__init__(config)
        self._logger = logging.getLogger("LQMT.FromSnort.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def __check_existence(self):
        """
        Checks the configured alert and pcap paths as well as the rule file for existence.

        :return: Boolean True/False indicator configured directory/file existence
        """
        # checks each directory in the configured snort alert paths
        for i in self._config.alert_paths:
            if not os.path.isdir(i):
                self._logger.error("Exiting - alert directory doesn't exists.")
                return False

        # checks each directory in the configured snort pcap capture paths
        for x in self._config.packets_paths:
            if not os.path.isdir(x):
                self._logger.error("Exiting - alert directory doesn't exists.")
                return False

        # checks each rules file in the configured rules list
        for y in self._config.rule_list:
            if not os.path.isfile(y):
                self._logger.error("Exiting - rule file(s) don't exist.")
                return False

        return True

    def __calculate_age_threshold(self):
        """
        Calculates the shifted date/time based on UTC now.  To be used for comparing file modified times.

        :return shift: Arrow object that represents now - the configured max age.
        """
        now = arrow.utcnow()
        second = ['s', 'sec', 'secs', 'second', 'seconds']
        minute = ['m', 'min', 'minute', 'minutes']
        hour = ['h', 'hr', 'hrs', 'hour', 'hours']
        day = ['d', 'day', 'days']
        week = ['w', 'week', 'weeks']
        month = ['mon', 'month', 'months']
        year = ['y', 'yr', 'yrs', 'year', 'years']

        cols = self._config.data_age.split(' ')
        if cols[0].isdigit():
            num = -1 * int(cols[0])
        else:
            raise ConfigurationError(
                "Unable to parse file age \"{0}\" expecting %d %s format (e.g. 2 weeks)".format(self._config.data_age))

        if cols[1] in second:
            shift = now.shift(seconds=num)
        elif cols[1] in minute:
            shift = now.shift(minutes=num)
        elif cols[1] in hour:
            shift = now.shift(hours=num)
        elif cols[1] in day:
            shift = now.shift(days=num)
        elif cols[1] in week:
            shift = now.shift(weeks=num)
        elif cols[1] in month:
            shift = now.shift(months=num)
        elif cols[1] in year:
            shift = now.shift(years=num)
        else:
            raise ConfigurationError(
                "Unable to determine time string in \"{0}\". Refer to documentation for accepted time strings.".format(self._config.data_age))

        return shift

    def __check_new_content(self, path_list):
        """
        Iterates through list of file paths/names to determine which have been modified since the configured max age.

        :param path_list: List of file paths and file names to check.
        :return: Set - contains file path/names for files modified more recent than configured maximum age.
        """
        ret = set()

        for i in path_list:
            for root, dirs, fnames in os.walk(i):
                for fname in fnames:
                    filepath = os.path.join(root, fname)
                    file_age = arrow.get(os.path.getmtime(filepath))
                    shift = self.__calculate_age_threshold()
                    if file_age > shift:
                        ret.add(filepath)

        return ret

    def __full_log_parse(self, logfile):
        """
        Code utilizes py parser to set up regular expressions for a Snort Alert File (full logging only).
        It is important to note this may need adjustment based on logging style chosen and fields for entries.

        :param logfile: Snort alert log file - from full logging configuration.
        :return ret: Dictionary containing parsed alert log entries.
        """
        i = 0
        ret = {}

        integer = pyp.Word(pyp.nums)
        ip_addr = (pyp.Combine(integer+'.'+integer+'.'+integer+'.'+integer)
                   + pyp.Suppress(pyp.Optional(":" + integer)))

        header = (pyp.Suppress("[**] [")
                  + pyp.Combine(integer + ":" + integer + ":" + integer)
                  + pyp.Suppress(pyp.SkipTo("[**]", include=True)))
        cls = (
            pyp.Suppress(pyp.Optional(pyp.Literal("[Classification:")))
            + pyp.Regex("[^]]*") + pyp.Suppress(']'))

        pri = pyp.Suppress("[Priority:") + integer + pyp.Suppress("]")
        date = pyp.Combine(
            integer+"/"+integer+'-'+integer+':'+integer+':'+integer+'.'+integer)
        src_ip = ip_addr + pyp.Suppress("->")
        dest_ip = ip_addr

        # TODO: In example, classification doesn't exist, but if inconsistent output won't parse right
        # TODO: Suppressed port information from extraction for now (not in ICMP entries)
        # TODO: might want to cascade matching -> on header, then match on IPs, then match on ports
        # bnf = header+cls+pri+date+src_ip+dest_ip
        bnf = header + pri + date + src_ip + dest_ip

        try:
            with open(logfile) as snort_logfile:
                for has_content, grp in itertools.groupby(
                        snort_logfile, key=lambda x: bool(x.strip())):
                    if has_content:
                        tmpStr = ''.join(grp)
                        fields = bnf.searchString(tmpStr)
                        if fields:
                            ret[i] = {}
                            ret[i]['file'] = logfile
                            ret[i]['text'] = tmpStr
                            ret[i]['matches'] = fields
                            i += 1
        except Exception as e:
            self._logger.warning("Unable to read file {0}. Exceptions={1}".format(logfile, e))

        return ret

    def __load_alert_ids(self):
        """
        Parses each rule file to extract the relevant Identifiers, actions, headers and pre-build a matching string.

        :return rules: Dictionary containing parsed Snort rules from configured rules files.
        """
        rules = {}

        for i in self._config.rule_list:
            # uses IDS tools library to extract rules
            rule_file = rule.parse_file(i)
            for x in rule_file:
                if x.enabled:
                    rules[x.sid] = {}
                    rules[x.sid]['sid'] = x.sid
                    rules[x.sid]['gid'] = x.gid
                    rules[x.sid]['rev'] = x.rev
                    rules[x.sid]['logmatch'] = "{0}:{1}:{2}".format(str(x.gid), str(x.sid), str(x.rev))
                    rules[x.sid]['action'] = x.action
                    rules[x.sid]['header'] = x.header

        self._logger.info("Extracted {0} rules from the Snort configuration.".format(str(len(rules))))

        return rules

    def __check_content_matches(self, parsed_log, snort_ids):
        """
        Compares the parsed Snort alert log field to identify matching Snort IDs.
        The full text of the alert entry and the SRC/DST IP addresses are then returned.

        :param parsed_log: Dictionary with each Snort alert log entry parsed for comparison.
        :param snort_ids: Dictionary with parsed Snort rule entries.
        :return: Dictionary containing final matched alert log entries and SRC/DST IP addresses.
        """
        ret_text = []
        ips = set()
        ret = {}

        for key, value in parsed_log.items():
            for x, y in snort_ids.items():
                # checks the gid:sid:rev for each rule against the parsed alert entry [0][0] with IDs
                if y['logmatch'] in value['matches'][0][0]:
                    ret_text.append(value['text'])
                    ips.add(value['matches'][0][-1])  # DST IP is in last list position
                    ips.add(value['matches'][0][-2])  # SRC IP is in second to last list position

        # full text is needed for writing non-parsed context into temporary files
        if ret_text:
            ret['text'] = ret_text

        # currently IPs used as an OR and not dependent on SRC/DST so returned as a unique list of all
        if ips:
            ret['ips'] = ips

        self._logger.info(
            "Found {0} matching alert entries and extracted {1} IP addresses".format(str(len(ret_text)), str(len(ips))))
        return ret

    def __find_file_matches(self, path_list, snort_ids):
        """
        Parses a list of alert files to identify new alert entries that match desired snort id's.
        New files are determined by comparing modified time to configured maximum age.

        :param path_list: List of alert files to check for new matches
        :param snort_ids: Parsed Snort rules that contains ID's for alert file matching
        :return: Filepaths, IP Addresses - Sets containing matching files and extracted IP addresses
        """
        ret_files = set()
        file_set = set()
        ip_set = set()
        prsd_log = {}

        # create a list of files that have new entries
        file_set = self.__check_new_content(path_list)
        for filepath in file_set:
            # Parses a snort alert log file to extract fields
            prsd_log = self.__full_log_parse(filepath)

            # compare the parsed alert log entries to match desired Snort IDs
            ret = self.__check_content_matches(prsd_log, snort_ids)

            # this allows a temporary alert file to be written that only contains full text for Snort ID matches
            if 'text' in ret:
                fname = os.path.basename(filepath)
                with open(self._config.result_path + '/' + fname, 'w') as f:
                    for lines in ret['text']:
                        f.write(lines + '\n')
                ret_files.add(self._config.result_path + '/' + fname)

            # SRC/DST IP addresses are extracted from the Snort log for future PCAP matching
            if 'ips' in ret:
                ip_set.update(ret['ips'])

        return ret_files, ip_set

    def __find_pcap_matches(self, path_list, ip_match):
        """
        Uses PyShark to filter PCAPs for packets that match passed in IP addresses.
        Upon completion temporary files are written that contain only matching packets.

        :param path_list: List containing the pcap files selected for comparing.
        :param ip_match: Set containing IP addresses to filter in the PCAPs.
        :return: ret - Set containing filepaths of temporarily written filtered pcap files.
        """
        ret = set()

        if not ip_match:
            return ret

        # TODO: for now only matches IP addresses, results in extra packets being grabbed since no protocol matching
        # Pop the first entry since it is a set
        filter_str = 'ip.addr==' + str(ip_match.pop())

        # if there are more IPs in the set, add to filter string as an OR
        for x in ip_match:
            filter_str += ' or ip.addr==' + str(x)

        # returns a list of only files modified newer than the maximum configured age
        file_set = self.__check_new_content(path_list)
        for filepath in file_set:
            # creates the temporary filename, %f used to add MS granularity
            now = arrow.utcnow()
            fname = self._config.result_path + '/' + now.strftime('%Y%m%d-%H%M%S%f') + '_filtered.pcap'

            try:
                # utilizing display_filter ensures only matching packets, output_file automatically creates a new file
                pcap = pyshark.FileCapture(filepath,
                                           display_filter=filter_str,
                                           output_file=fname)

                # must load the packet matches to get output_file to write
                pcap.load_packets()
                if len(pcap) > 0:
                    ret.add(fname)  # if matches found, add temp filename for future writing results
                    self._logger.info("Successfully matched {0} packets from {1}".format(str(len(pcap)), filepath))
                else:  # pyshark creates file even if empty so remove
                    os.remove(fname)
                    self._logger.info("No matching packets from {0}".format(filepath))
                pcap.close()
            except Exception as e:
                self._logger.warning("Exception loading {0} as PCAP = {1}".format(filepath, e))

        return ret

    def process(self, alert=None):
        """
        Process function. Handles the processing of data for the tool.
        """
        file_set = set()
        ip_set = set()
        pcap_set = set()
        ret = {}
        file_list = []

        if not self.__check_existence():
            # failure logged in function
            return

        # TODO: only supports "full" logging mode for snort
        # TODO: fast, unified2, etc. unsupported

        if self._config.mode == 'full':
            # zip files with modifications more recent than configured

            # combines the alert and pcap paths
            file_list = copy.deepcopy(self._config.alert_paths)
            file_list.extend(self._config.packets_paths)

            # checks each directory to find the "new" files into a set
            file_set = self.__check_new_content(file_list)

            # write all selected files to a zip file, don't remove originals
            self.write_results(file_set, rm_file=False)

        elif self._config.mode == 'match':
            # match mode parses snort alert files and pcaps to match snort ids and IP address packets

            # read the updating rule file to extract rule context
            ret = self.__load_alert_ids()

            # parses through the snort alert logs to match snort id and return list of associated SRC/DST IP addresses
            # following this, snort alert matches are in new files in the configured result path
            file_set, ip_set = self.__find_file_matches(self._config.alert_paths, ret)

            # parse each pcap file to identify packets with IP address matches
            # following this, pcap packet matches are in new files in the configured result path
            pcap_set = self.__find_pcap_matches(self._config.packets_paths, ip_set)

            # zip all temporary alert and pcap match files and remove the temporary files
            file_set.update(pcap_set)
            self.write_results(file_set, rm_file=True)

        else:  # Unknown capture mode
            self._logger.error("Unknown configured mode = {}".format(self._config.mode))

    def commit(self):
        pass

    def cleanup(self):
        pass

    def write_results(self, file_set, rm_file=False):
        """
        Writes the final context matches to a zip file.  To be used to create an upload file.

        :param file_set: The final list of files that have content to be zipped for sharing.
        :param rm_file: Boolean flag to delete the original file after zipping.
        :return: None
        """
        try:
            if not file_set:
                self._logger.info("No Snort files identified")
                return

            # create file name based on date/time with %f used to add MS
            now = arrow.utcnow()
            fname = now.strftime('%Y%m%d-%H%M%S%f') + '_snort_logs.zip'
            filename = self._config.result_path + '/' + fname

            # create a zip file from the passed in list of files
            with ZipFile(filename, 'w') as zip:
                for x in file_set:
                    # TODO: currently does not maintain original sub folders, but flattens the zip contents
                    # TODO: with conflicting name, ZipFile appears to force write
                    no_path = os.path.basename(x)  # this removes the subfolders from the name
                    zip.write(x, arcname=no_path)

            self._logger.info(
                "Successfully matched {0} files. Zip output created at {1}".format(str(len(file_set)), filename))

            # allows users to write temporary files and them remove after successful zip
            if rm_file:
                for y in file_set:
                    os.remove(y)
                self._logger.info("Successfully deleted original files")

            # TODO: there is a 15 MB CFM upload limit, handle that at all?
        except Exception as e:
            self._logger.error("Unable to create zipped results. Exception={0}".format(e))
