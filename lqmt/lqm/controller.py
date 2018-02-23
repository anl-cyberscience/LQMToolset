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
        self.pull()
        self.push()

    def push(self):
        """
        Function for initializing and running all the user defined "from" tools.
        """
        alert_files = self._initialize()
        if alert_files:
            for data, unparsed_metadata in alert_files:
                metadata = self._parsemeta(unparsed_metadata)
                if metadata:
                    filters = self._config.getSourceFilters()
                    if filters:
                        if filters.checkAllFilters(metadata):
                            self._parse(data, metadata)
                    else:
                        self._parse(data, metadata)
        self._chainCleanup()

    def pull(self):
        # TODO: All tool functions contained to this function. Should give pull tools their own chain type and break
        # out the other functions out to the chain class. Similar to how it's done for push tools now.
        for chain in self.toolChains['pull']:
            chain.pull_process()

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
        :return: Returns filesToProcess object, which is defined in sourcedir.py. It's an object that has a custom
        __iter__ method that is used to traverse the top level alert directories provided by the user in user config
        """

        filesToProcess = None

        for chain in self.toolChains['push']:
            if chain._enabled:
                chain.initialize()
            else:
                self._logger.error("Toolchain '{0}' is disabled due to user configuration, or because no tools were "
                                   "correctly configured for the toolchain.".format(chain.getName()))
            chain.updateEnabled()

        if self._config.getSources():
            for src in self._config.getSources():
                self.src = src
                filesToProcess = src.getFilesToProcess()

        return filesToProcess

    def _parse(self, data, metadata):
        """
        Defines all parsers needed based on the metadata given. Once defined, the parsers are used to parse alert data
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
                    for chain in self.toolChains['push']:
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
            if self._post_filter_pass(alert):
                self.numAlerts += 1
                isWL = alert.isWhitelisted(self._config.getWhitelist())
                chain.process(alert, isWL, datafile, metadata)
                chain.fileDone()

    def _post_filter_pass(self, alert):
        """
        Pass through filter for post-processed data.
        :param alert: Alert object
        :return: Bool
        """
        if not self._filter_check(alert._indicatorType, 'type'):
            return False
        if not self._filter_check(alert._directSource, 'source'):
            return False
        if not self._filter_check(alert._action1, 'action'):
            return False
        if not self._filter_check(alert._restriction, 'restriction'):
            return False

        return True
    
    def _filter_check(self, alert_value, filter_type):
        """
        Function to properly check filters.
        :param alert_value: The given alert value needed to check
        :param filter_type: Type of filter to check for
        :return: Bool
        """
        if isinstance(alert_value, str):
            if alert_value.upper() in self._config._filter['exclude'][filter_type]:
                return False
        return True

    def _chainCleanup(self):
        """
        Cleans up tools that are done processing and logs statistics on amount of processed alerts.
        """

        for chain in self.toolChains['push']:
            if chain.isEnabled():
                chain.commit()
                chain.cleanup()

        for src in self._config.getSources():
            src.logStatistics(self.numAlerts)