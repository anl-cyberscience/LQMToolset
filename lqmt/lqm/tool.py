import re
import logging
from lqmt.lqm.data import AlertAction
from lqmt.lqm.unprocessed import UnprocessedAlertHandler
from lqmt.lqm.exceptions import ConfigurationError


class ToolConfig():
    """Base class for all tool configs"""

    def __init__(self, configData, csvToolInfo, unhandledCSV):
        self._name = configData['name']  # the tool's name
        self._enabled = self._name != None  # whether or not the tool is enabled
        self._unprocessedHandler = None  # The handler to use if there is an unprocessed alert
        if ('unprocessed_file' in configData):
            if (csvToolInfo == None or unhandledCSV == None):
                raise ConfigurationError()
            cfg = {}
            cfg['file'] = configData['unprocessed_file']
            cfg.update(unhandledCSV)
            self._unprocessedHandler = UnprocessedAlertHandler(csvToolInfo.create(cfg, None, None))

    def getName(self):
        """
        :return: Returns tool named defined in the userconfig
        """
        return self._name

    def isEnabled(self):
        return self._enabled

    def disable(self):
        self._enabled = False

    def getActionsToProcess(self):
        return self._actionsToProcess

    def getUnprocessedHandler(self):
        return self._unprocessedHandler


class Tool():
    """The base class for all tools."""

    def __init__(self, config, alertActions):

        self._config = config  # the configuration object
        self._alertActions = set(alertActions)  # The alert actions this tool handles
        self.toolName = ""  # The name of the tool defined by the tools class

    def getConfig(self):
        return self._config

    def isEnabled(self):
        return self._config.isEnabled()

    def disable(self):
        """Disable the tool"""
        self._config.disable()

    def getName(self):
        nm = self._config.getName()
        if (nm):
            return nm
        else:
            return "UNKNOWN-{0}".format(type(self).__name__)

    def unprocessed(self, alert):
        """The specified alert has not been processed when it should have been>  This gives the opportunity to log this info or report it to the user."""
        uph = self._config.getUnprocessedHandler()
        if (uph != None):
            uph.unprocessed(alert)

    def getActionsToProcess(self):
        return self._alertActions

    def initialize(self):
        uph = self._config.getUnprocessedHandler()
        if (uph != None):
            uph.initialize()

    def fileBegin(self):
        NotImplementedError

    def fileDone(self):
        NotImplementedError

    # Will only be called for alerts this tool can process
    def process(self, alert):
        """Process the alert."""
        NotImplementedError

    def commit(self):
        """Called at the end of processing to allow the tool to perform any finalization"""
        NotImplementedError

    def cleanup(self):
        """called after commit to perform any cleanup necessary."""
        NotImplementedError

    def is_valid_ipv6(self, ip):
        """Validates IPv6 addresses."""
        pattern = re.compile(r"""
            ^
            \s*                         # Leading whitespace
            (?!.*::.*::)                # Only a single whildcard allowed
            (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
            (?:                         # Repeat 6 times:
                [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            ){6}                        #
            (?:                         # Either
                [0-9a-f]{0,4}           #   Another group
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                [0-9a-f]{0,4}           #   Last group
                (?: (?<=::)             #   Colon iff preceeded by exacly one colon
                 |  (?<!:)              #
                 |  (?<=:) (?<!::) :    #
                 )                      # OR
             |                          #   A v4 address with NO leading zeros
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                (?: \.
                    (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                ){3}
            )
            \s*                         # Trailing whitespace
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(ip) is not None

    def is_valid_ipv4(self, ip):
        """Validates IPv4 addresses.
        """
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip) is not None


class ToolChain():
    """A ToolChain is a list of tools that pass data from one to the next"""

    def __init__(self, tools, name, enabled):
        self._tools = tools
        self._name = name
        self._enabled = enabled
        self._logger = logging.getLogger("LQMT.Tools")
        self._actionsToProcess = None
        for tool in self._tools:
            if (self._actionsToProcess == None):
                self._actionsToProcess = tool.getActionsToProcess()
            else:
                self._actionsToProcess &= tool.getActionsToProcess()
        self._alertsProcessed = 0
        self._alertsNotProcessed = 0

    def isEnabled(self):
        return self._enabled

    def initialize(self):
        """called by the controller at the beginning of processing to allow the tool chain to initialize itself."""
        # tell all the tools to initialize
        for tool in self._tools:
            tool.initialize()

    def fileBegin(self):
        """A new file is about to be processed."""
        if self.isEnabled():
            for tool in self._tools:
                tool.fileBegin()

    def fileDone(self):
        """All alerts from the current file have been processed."""
        if self.isEnabled():
            for tool in self._tools:
                tool.fileDone()

    def process(self, data, isWhitelisted, datafile, meta):
        """
        Process the alert data using each tool in the toolchain

        :param data: the processed alert data in the intermediate format
        :param isWhitelisted: indicates if the alert data is whitelisted or not
        :param datafile: the directory location of the processed alert datafile. Currently only used with FlexText
         because the alert has to be reprocessed for FlexText
        """
        if self.isEnabled():
            # if the alert can be processed by this toolchain, then process it
            if data.getAction() in self._actionsToProcess or AlertAction.get('All') in self._actionsToProcess:
                # if indicator isn't whitelisted, proceed with processing. Otherwise ignore processing
                # and log the whitelist block.
                if isWhitelisted is False:
                    self._alertsProcessed += 1
                    for tool in self._tools:
                        # FlexText requires the datafile instead of the processed data.
                        if tool.toolName == "FlexText":
                            tool.process(datafile, meta)
                        else:
                            tool.process(data)
                else:
                    self._logger.info(
                        "Alert not processed. IP Indicator is whitelisted. Whitelisted IP:{0}".format(
                            data.getIPToBlock()))
            else:
                self._alertsNotProcessed += 1

    def commit(self):
        """Called at the end of processing to allow the tool chain to perform any finalization"""
        if self.isEnabled():
            for tool in self._tools:
                tool.commit()

    def cleanup(self):
        """Called after commit to perform any cleanup"""
        if self.isEnabled():
            self._logger.info(
                "Alerts processed:={0} AlertsNotProcessed={1}".format(self._alertsProcessed, self._alertsNotProcessed))
            for tool in self._tools:
                tool.cleanup()

    def updateEnabled(self):
        """Update the enabled state of this tool chain by checking all of its tools.  If any are disabled, disable the chain, too."""
        en = self.isEnabled()
        if (not en):
            return
        for tool in self._tools:
            if (not tool.isEnabled()):
                en = False
        self._enabled = en

    def getName(self):
        return self._name

    def printTools(self):
        toolStr = ""
        comma = " "
        for tool in self._tools:
            toolStr += comma
            toolStr += tool.getName()
            comma = ", "
        self._logger.debug(toolStr)
