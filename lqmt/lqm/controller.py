import ast
import logging
from lqmt.lqm.logging import LQMLogging
from .config import LQMToolConfig


# based on filename, place file either in the metafiles dict or the datafiles list
# NOTE: Assumes metafiles begin with . and datafiles do not.

class LQMToolController:
    def __init__(self, configfile):
        """
        Controller for LQMT.
        :param configfile: User configuration file
        """

        self._logger = logging.getLogger("LQMT.Controller")
        self._logger.info("Starting LQMTool")

        self._config = LQMToolConfig(configfile)
        self.toolChains = self._config.getToolChains()
        self.numAlerts = 0
        self.src = None

    def run(self):
        """
        Main function of the controller. Runs through the various methods used to gather alert files, parse them,
        and send the parsed alert data to the various tools.
        """

        alert_files = self._initialize()

        for data, unparsed_metadata in alert_files:
            metadata = self._parsemeta(unparsed_metadata)
            if metadata:
                self._parse(data, metadata)
        self._chainCleanup()

    def _parsemeta(self, metafile):
        """
        Parses metadata files
        :param metafile: Path to metadata file
        :return: Returns parsed metadata if the file path is valid. If not, then it returns None
        """

        try:
            f = open(metafile, 'r')
            meta = ast.literal_eval(f.read())
            f.close()
            return meta
        except Exception as inst:
            self._logger.error('An exception occurred while opening/parsing {0}:'.format(metafile))
            self._logger.error(str(inst))
            return None

    def _initialize(self):
        """
        Initializes LQMT. This includes initializing toolchains and their respective tools, and then getting all alert
        files specified from sources defined in the user configuration.
        :return: Returns alert files
        """

        files = None

        for chain in self.toolChains:
            if chain.isEnabled():
                chain.initialize()
            chain.updateEnabled()

        for src in self._config.getSources():
            self.src = src
            files = src.getFilesToProcess()

        return files

    def _parse(self, data, metadata):
        """
        Defines all parses needed based on the metadata given. Once defined, the parsers are used to parse alert data
        and pass the data to tools.
        :param data: Alert data
        :param metadata: Alert metadata
        """

        parser = self._config.getParser(metadata["PayloadFormat"])

        try:
            if parser is not None:
                # tell each chain there is a new file
                alerts = parser.parse(data, metadata)
                if alerts:
                    for chain in self.toolChains:
                        if chain.isEnabled():
                            chain.fileBegin()
                            self._process_alerts(alerts, chain, data, metadata)
                            self.src.processed(data)
                else:
                    self._logger.error("Processing error occurred. No processed alert data returned to LQMT.")
        except Exception as e:
            msg = "An exception occurred while processing file '{0}'".format(data)

            if not LQMLogging.isDebug():
                self._logger.error(msg)
            else:
                self._logger.exception(msg)
            self._logger.error(str(e))

    def _process_alerts(self, alerts, chain, datafile, metadata):
        """
        Takes alert data and passes it to active toolchains and their respective tools.
        :param alerts: Alert data
        :param chain: Toolchain
        """

        for alert in alerts:
            self.numAlerts += 1
            isWL = alert.isWhitelisted(self._config.getWhitelist())
            chain.process(alert, isWL, datafile, metadata)
            chain.fileDone()

    def _chainCleanup(self):
        """
        Cleans up tools that are done processing and logs statistics on amount of processed alerts.
        """

        for chain in self.toolChains:
            if chain.isEnabled():
                chain.commit()
                chain.cleanup()

        for src in self._config.getSources():
            src.logStatistics(self.numAlerts)