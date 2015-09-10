#!/usr/bin/env python3

def main():
    import sys

    #need to put this check early so any imports farther down don't trigger an exception
    req_version=(3,2)
    cur_version = sys.version_info
    if(cur_version <= req_version):
        print("Your python version {0}.{1}.{2}-{3} is too old.  LQMTools requires at least version 3.2".format(cur_version[0],cur_version[1],cur_version[2],cur_version[3]))
        sys.exit(1)

    import logging
    from lqmt.lqm.controller import LQMToolController
    import argparse
    from lqmt.lqm.logging import LQMLogging

    parser = argparse.ArgumentParser()
    parser.add_argument('user_config_file',help='The user configuration file')
    args=parser.parse_args()

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

if __name__ == '__main__':
    main()
