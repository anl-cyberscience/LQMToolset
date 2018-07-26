"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
from lqmt.lqm.tool import PullTool


class FromMattermost(PullTool):
    def __init__(self, config):
        """
        FromToolName description
        :param config: configuration file
        """
        super().__init__(config)
        self._logger = logging.getLogger("LQMT.FromMattermost.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def process(self, alert=None):
        """
        Process function. Handles the processing of data for the tool.
        """
        print("Running FromMattermost")
        self.write_results('test')

    def commit(self):
        pass

    def cleanup(self):
        pass

    def write_results(self, file, meta=None):
        """

        :param file:
        :param meta:
        :return:
        """
        try:
            if not file:
                return

            fname = 'tbd.txt'
            filename = self._config.result_path + '/' + fname

            with open(filename, 'w') as f:
                f.write("Testing output")
            self._logger.info("Successfully wrote output file")

        except Exception as e:
            self._logger.error("Unable to write results. Exception={0}".format(e))
