import os
import ast
from .config import LQMToolConfig
import logging
from lqmt.lqm.logging import LQMLogging


# based on filename, place file either in the metafiles dict or the datafiles list
# NOTE: Assumes metafiles begin with . and datafiles do not. 

class LQMToolController():
    def __init__(self, configfile):
        self._config = LQMToolConfig(configfile)
        self._logger = logging.getLogger("LQMT.Controller")
        logging.getLogger("LQMT").info("Starting LQMTool")

    def _parsemeta(self, metafile):
        try:
            f = open(metafile, 'r')
            meta = ast.literal_eval(f.read())
            f.close()
            return meta
        except Exception as inst:
            self._logger.error('An exception occurred while opening/parsing {0}:'.format(metafile))
            self._logger.error(str(inst))
            return None

    def run(self):
        """Run LQMTool"""
        # initialize tool chains
        toolChains = self._config.getToolChains()
        numAlerts = 0

        for chain in toolChains:
            if (chain.isEnabled()):
                chain.initialize()
            chain.updateEnabled()  # if there was an error during initialization that disabled a tool
        # for each source
        for src in self._config.getSources():
            # get files to process
            files = src.getFilesToProcess()
            for datafile, metafile in files:
                # for each datafile/metfafile set
                meta = self._parsemeta(metafile)
                if (meta):
                    # get the parser for the payload format of this file.
                    # Note that parser is defined by the payload format of the given file.
                    parser = self._config.getParser(meta["PayloadFormat"])
                    try:
                        if (parser != None):
                            # tell each chain there is a new file
                            for chain in toolChains:
                                if (chain.isEnabled()):
                                    chain.fileBegin()
                            # parse the file and get the alerts
                            alerts = parser.parse(datafile, meta)
                            for alert in alerts:
                                # tell each chain to process each alert
                                numAlerts += 1
                                isWL = alert.isWhitelisted(self._config.getWhitelist())
                                for chain in toolChains:
                                    if chain.isEnabled():
                                        chain.process(alert, isWL, datafile, meta)
                            # notify each chain the file is done
                            for chain in toolChains:
                                if (chain.isEnabled()):
                                    chain.fileDone()
                            # tell the source that the file was processed so it can take any action needed
                            src.processed(datafile)
                    except Exception as e:
                        msg = "An exception occurred while processing file '{0}'".format(datafile)
                        if (not LQMLogging.isDebug()):
                            self._logger.error(msg)
                        else:
                            self._logger.exception(msg)
                        self._logger.error(str(e))
        # after all files are processed, tell each chain to commit themselves
        for chain in toolChains:
            if (chain.isEnabled()):
                chain.commit()
        for src in self._config.getSources():
            src.logStatistics(numAlerts)
        # finally, tell each chain to perform any cleanup necessary
        for chain in toolChains:
            if (chain.isEnabled()):
                chain.cleanup()
