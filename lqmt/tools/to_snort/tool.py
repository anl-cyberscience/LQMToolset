"""
Created on March 13, 2018

@author: grjohnson
"""
import logging
import os
import copy
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToSnort(Tool):
    def __init__(self, config):
        """
        ToSnort tool.  Used to insert Snort rules into a Snort configuration.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger("LQMT.ToSnort.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def __setup_snort_configs(self):
        """
        Sets up the configuration files for the Snort installation.
        First step is to confirm that the snort configuration file exists.
        Next step is to confirm/create the configured rules files exist.
        Finally, if the rules files are not included in the snort configuration file - add it.
        :return Boolean: True is Snort configs are correct.  False if configs don't exist at configured path.
        """
        rule_files = []
        rule_needed = []

        # check for snort.conf existence
        for i in self._config.snort_cfg_filepaths:
            file_path = i + '/' + self._config.snort_cfg_filename
            if not os.path.isfile(file_path):
                self._logger.error(
                    "Exiting Snort configuration file doesn't exist {0}: No rules written".format(file_path))
                return False

        # check if rules file exists
        for i in self._config.rule_paths:
            file_path = i + '/' + self._config.rule_filename
            if not os.path.isfile(file_path):
                # if not create it
                open(file_path, 'w').close()
            rule_files.append(file_path)

        # check if rules file exists in the snort.conf
        for i in self._config.snort_cfg_filepaths:
            rule_needed = copy.deepcopy(rule_files)
            file_path = i + '/' + self._config.snort_cfg_filename
            with open(file_path, "r") as conf_file:
                for line in conf_file:
                    for x in rule_files:
                        if 'include ' + x in line:
                            rule_needed.remove(x)
                        if not rule_needed:  # speed this up by quitting once all are found
                            break

            # TODO: find section 7 for site specific rules or add to local rules only
            if rule_needed:
                with open(file_path, "a") as conf_file:
                    conf_file.write('\n\n')
                    for x in rule_needed:
                        self._logger.info("Added rule file to Snort configuration " + x)
                        conf_file.write('# Cyber Fed Model added rules file\n')
                        conf_file.write('include ' + x + '\n')

        return True

    def process(self, alerts):
        """
        Process function.  Handles the processing of data for the tool.
        Once completed, the rules file(s) contain the new alerts, have unique entries,
        and is smaller than the maximum count if configured to check.

        Important pre-conditions:
        - Currently only supports StixFile data objects from the Parser
        - The rules dictionary from the parser must have a 'snort' entry

        :param alerts:
        :return None:
        """
        # TODO: STIX Snort Specification allows -- Event Filters / Rate Filters / Event Suppression
        file_lines = []
        ap_char = []

        # compare to list of compatible objects
        if type(alerts).__name__ not in self._config.compatible_types:
            self._logger.warning("Unsupported Object Type {0}: No rules written".format(type(alerts).__name__))
            return

        # should confirm that snort is in rules dictionary
        snort_rules = alerts.getRules('snort')  # Requires the user to have configured parser for snort
        if not snort_rules:
            self._logger.warning("Snort rules do not exist in data object.")
            return

        try:
            x = self.__setup_snort_configs()
            if not x:
                # logging is performed in the function call
                return

            # Processing loop for each configured rules file
            for i in self._config.rule_paths:
                file_path = i + '/' + self._config.rule_filename

                if self._config.mode == 'full':
                    with open(file_path, 'w') as rule_file:
                        rule_file.write("".join(snort_rules))

                    # when in full overwrite mode, configured setting is ignored
                    if len(snort_rules) > self._config.max_rules:
                        self._logger.warning("Maximum rules configuration in ignored in Full mode.")

                    self._logger.info(
                        "Added {0} rule entries to {1}".format(str(len(snort_rules)), file_path))

                elif self._config.mode == 'append':
                    # READ: existing file for processing
                    with open(file_path, 'r') as rule_file:
                        file_lines = rule_file.readlines()

                    # this is only applicable if coming from STIX and no '\n'
                    # add \n to each new rule to compare to existing rules
                    # ap_char = list(x + '\n' for x in snort_rules)
                    for x in snort_rules:
                        if x[-1] != '\n':
                            ap_char.append(x+'\n')
                        else:
                            ap_char.append(x)

                    # utilize set to create unique list of new rules and existing rules
                    new_rule_list = set(ap_char)
                    curr_file_list = set(file_lines)

                    # MAXIMUM: check total number of new rules against the maximum allowed
                    if self._config.max_rules != -1:
                        # calculate if a the new combined set of unique entries is > maximum
                        new_file_list = copy.deepcopy(curr_file_list)
                        new_file_list.update(new_rule_list)
                        new_rules = len(new_file_list)
                        if new_rules > self._config.max_rules:
                            # if combination is too large, remove first entries to create new list
                            new_start = new_rules - self._config.max_rules
                            self._logger.info(
                                "Maximum Rules in the file, removing {0} entries".format(str(new_start)))
                            temp = list(curr_file_list)[new_start:]
                            temp2 = set(temp)
                            temp2.update(new_rule_list)
                            new_file = list(temp2)
                        else:
                            # important - if under threshold use the new list to write to file
                            new_file = list(new_file_list)
                    else:
                        # if not checking # of rules, create new list and set to write to file
                        curr_file_list.update(new_rule_list)
                        new_file = list(curr_file_list)

                    # TODO: Need to test and confirm no duplicate entries, max rules, etc.
                    # WRITE: update the rules file with remaining new rules
                    with open(file_path, 'w') as rule_file:
                        rule_file.write("".join(new_file))

                    self._logger.info(
                        "Added {0} rule entries to {1}".format(str(len(new_rule_list)), file_path))
                else:
                    self._logger.warning(
                        "No rules added to {0}. Unknown mode={1}".format(file_path, self._config.mode))

            # TODO: handle the auto restart snort command?
        except Exception as e:
            self._logger.error("Error while updating Snort Rules. Exception={0}".format(e))

    def commit(self):
        pass

    def cleanup(self):
        pass
