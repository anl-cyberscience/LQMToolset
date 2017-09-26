import logging
import os.path
import time
from logging import FileHandler, Formatter
from lqmt.lqm.exceptions import ConfigurationError


class LQMLogging(object):
    """Logging helper class"""

    # by default the debug flag is off
    _debug = False


    @staticmethod
    def isDebug():
        return LQMLogging._debug

    @staticmethod
    def lowerconfig(config):
        """
        Method that makes all keys in the config dict lowercase. Prevents errors where users supply old 
        config style forlogging.
        :param config: Dict containing configuration data
        :return: Returns config dict with all of it's keys in lowercase.
        """
        newconf = {}
        for key in config.keys():
            newconf[key.lower()] = config[key]

        del config
        return newconf

    def __init__(self, config):
        """Initialize the logging system from the configuration"""

        # TODO: use ezlog to be consistent with other tools in logging
        formatter = Formatter(fmt='%(asctime)s %(name)s %(levelname)s:%(message)s')
        rootLogger = logging.getLogger()
        active = True
        config = self.lowerconfig(config)

        if 'active' in config:
            active = bool(config['active'])

        if active and not len(rootLogger.handlers):
            if 'debug' in config:
                LQMLogging._debug = config['debug']
            else:
                LQMLogging._debug = False

            logger = logging.getLogger('LQMT')
            if not LQMLogging._debug:
                logger.setLevel(logging.INFO)
            else:
                logger.setLevel(logging.DEBUG)

            if 'dailyrotation' in config and config['dailyrotation'] is True:
                rotation = time.strftime("_%Y-%m-%d")
            else:
                rotation = ""

            if 'logfilebase' in config:
                lfb = config['logfilebase']

                ldir = os.path.dirname(lfb)
                if not os.path.exists(ldir):
                    os.makedirs(ldir, 0o755, True)

                # create handlers/files for error, info, and debug (if necessary)
                errHandler = FileHandler("{0}{1}.err.log".format(lfb, rotation))
                errHandler.setLevel(logging.ERROR)
                errHandler.setFormatter(formatter)
                rootLogger.addHandler(errHandler)

                infoHandler = FileHandler("{0}{1}.info.log".format(lfb, rotation))
                infoHandler.setLevel(logging.INFO)
                infoHandler.setFormatter(formatter)
                rootLogger.addHandler(infoHandler)

                if LQMLogging._debug:
                    debugHandler = FileHandler("{0}{1}.debug.log".format(lfb, rotation))
                    debugHandler.setLevel(logging.DEBUG)
                    debugHandler.setFormatter(formatter)
                    rootLogger.addHandler(debugHandler)

                # The ft handler creates a separate logger for FlexTransform errors
                # There were some files that caused a large number of FlexTransform errors and polluted the regular log
                # files. If it is determined that those issues are gone, then this can be removed
                ftHandler = FileHandler("{0}{1}.ft.log".format(lfb, rotation))
                ftHandler.setFormatter(formatter)
                logger = logging.getLogger('FlexTransform')
                logger.addHandler(ftHandler)
                logger.propagate = False
            else:
                logger.error("logfilebase must be specified in configuration")
                raise ConfigurationError("Logfilebase parameter missing")
