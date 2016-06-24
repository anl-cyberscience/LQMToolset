import logging
import time
import sys
from lqmt.lqm.controller import LQMToolController
from lqmt.lqm.logging import LQMLogging


class LQMT(object):
    """
    API for LQMT. Currently a basic implementation allowing the ability to add a user configuration and
    the ability to run LQMT against it.
    """

    def __init__(self):
        self.logger = logging.getLogger("LQMT")
        self.user_config = ""

    def run(self, config=None):
        """
        Runs LQMT against user configuration.
        :param config: can supply directory path to user config directly here. Config file must be in toml format.
        """
        if config:
            self.user_config = config

        try:
            controller = LQMToolController(self.user_config)

        except Exception as e:
            if not LQMLogging.isDebug():
                self.logger.error("An error occurred during configuration:")
            else:
                self.logger.exception("An error occurred during configuration:")
            self.logger.error(str(e))
            sys.exit(1)

        try:
            controller.run()

        except Exception as e:
            if not LQMLogging.isDebug():
                self.logger.error("An error occurred during processing:")
            else:
                self.logger.exception("An error occurred during processing:")
            self.logger.error(str(e))
        logging.getLogger("LQMT").info("LQMTool done. Process time: " + str(time.process_time()))

    def add_config(self, config):
        """
        Adds user configuration file to be used when running LQMT
        :param config: Directory path to configuration file. Configuration file must be in TOML format.
        """

        self.user_config = config


def main():
    """
    /lqmt/main.py will be migrated here for the sake of consistency.
    """
    pass

