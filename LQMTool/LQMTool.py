import sys
import logging
from lqm.controller import LQMToolController
import argparse
from lqm.logging import LQMLogging

parser = argparse.ArgumentParser()
parser.add_argument('user_config_file',help='The user configuration file')
args=parser.parse_args()

if __name__ == '__main__':
    logger = logging.getLogger("LQMT")
    try:
        controller=LQMToolController(args.user_config_file)
    except Exception as e:
        if(not LQMLogging.isDebug()):
            logger.error("An error occurred during configuration:")
        else:
            logger.exception("An error occurred during configuration:")
        logger.error(str(e))
        sys.exit(1)
    try:
        controller.run()
    except Exception as e:
        if(not LQMLogging.isDebug()):
            logger.error("An error occurred during processing:")
        else:
            logger.exception("An error occurred during processing:")
        logger.error(str(e))
    logging.getLogger("LQMT").info("LQMTool done")
