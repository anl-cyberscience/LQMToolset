import argparse
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

    def __init__(self, config=None):
        self.logger = logging.getLogger("LQMT")
        self.user_config = config

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

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
        logging.getLogger("LQMT").info("Process complete. Process time: " + str(time.process_time()))

    def add_config(self, config):
        """
        Adds user configuration file to be used when running LQMT
        :param config: Directory path to configuration file. Configuration file must be in TOML format.
        """
        self.user_config = config


def main():
    cur_version = sys.version_info
    if cur_version <= (3, 2):
        print("Your python version {0}.{1}.{2}-{3} is too old.  LQMTools requires at least version 3.2".format(
            cur_version[0], cur_version[1], cur_version[2], cur_version[3]
        ))
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Parse CTI data and make it actionable in endpoint defense tools.")
    parser.add_argument('user_config_file', help='The path to the user configuration file. ')
    args = parser.parse_args()

    with LQMT(args.user_config_file) as lqmt:
        lqmt.run()

if __name__ == '__main__':
    main()
