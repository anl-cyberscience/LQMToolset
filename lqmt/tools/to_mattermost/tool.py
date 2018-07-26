"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToMattermost(Tool):
    def __init__(self, config):
        """
        ToMattermost tool.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger("LQMT.ToMattermost.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def process(self, alerts):
        """
        Process function.  Handles the processing of data for the tool.

        :param alerts:
        :return None:
        """
        if alerts.getBinFile() is not None:
            print("ToMattermost process")

    def commit(self):
        pass

    def cleanup(self):
        pass
