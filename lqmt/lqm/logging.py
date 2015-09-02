from logging import FileHandler, Formatter
import logging
import os.path
from lqmt.lqm.exceptions import ConfigurationError

class LQMLogging(object):
    """LOgging helper class"""
    
    #by default the debug flag is off
    _debug=False
    @staticmethod
    def isDebug():
        return LQMLogging._debug

    def __init__(self, config):
        """Initialize the logging system from the configuration"""
        
        #TODO: use ezlog to be consistent with other tools in logging
        formatter = Formatter(fmt='%(asctime)s %(name)s %(levelname)s:%(message)s')
        rootLogger=logging.getLogger()
        if('Debug' in config):
            LQMLogging._debug=config['Debug']
        else:
            LQMLogging._debug=False

        logger = logging.getLogger('LQMT')
        logger.setLevel(logging.INFO)

        if('LogFileBase' in config):
            lfb=config['LogFileBase']
        
            ldir=os.path.dirname(lfb)
            if(not os.path.exists(ldir)):
                os.makedirs(ldir, 0o755, True)

            #create handlers/files for error, info, and debug (if necessary)
            errHandler=FileHandler("{0}.err.log".format(lfb))
            errHandler.setLevel(logging.ERROR)
            errHandler.setFormatter(formatter)
            rootLogger.addHandler(errHandler)
            
            infoHandler=FileHandler("{0}.info.log".format(lfb))
            infoHandler.setLevel(logging.INFO)
            infoHandler.setFormatter(formatter)
            rootLogger.addHandler(infoHandler)

            if(LQMLogging._debug):
                debugHandler=FileHandler("{0}.debug.log".format(lfb))
                debugHandler.setLevel(logging.DEBUG)
                debugHandler.setFormatter(formatter)
                rootLogger.addHandler(debugHandler)

            #The ft handler creates a separate logger for FlexTransform errors
            #There were some files that caused a large number of FlexTransform errors and polluted the regular log files
            #If it is determined that those issues are gone, then this can be removed
            ftHandler=FileHandler("{0}.ft.log".format(lfb))
            ftHandler.setFormatter(formatter)
            logger = logging.getLogger('FlexTransform')
            logger.addHandler(ftHandler)
            logger.propagate=False
        else:
            logger.error("LogFileBase must be specified in configuration")
            raise ConfigurationError()
