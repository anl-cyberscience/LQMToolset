import logging
from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.exceptions import ConfigurationError


class SplunkConfig(ToolConfig):

    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.Splunk.{0}".format(self.getName()))

        if 'host' in configData:
            self.host = configData['host']
        else:
            raise ConfigurationError(
                "Missing the 'host' parameter in the Splunk tool named: {0}".format(self.getName())
            )

        if 'port' in configData:
            self.port = configData['port']
        else:
            self.logger.info("The 'port' parameter wasn't specified in your config. Using the default value of 8089.")
            self.port = 8089

        if 'username' in configData:
            self.username = configData['username']
        else:
            raise ConfigurationError(
                "Missing the 'username' parameter in the Splunk tool named: {0}".format(self.getName())
            )

        if 'password' in configData:
            self.password = configData['password']
        else:
            raise ConfigurationError(
                "Missing the 'password' parameter in the Splunk tool named: {0}".format(self.getName())
            )

        if 'cert_check' in configData:
            self.cert_check = configData['cert_check']
        else:
            self.logger.info(
                "The 'cert_check' parameter wasn't specified in your config. Defaulting to a value of True, which will"
                "require a check for a valid certificate on your system before connecting to your Splunk instance."
            )
            self.cert_check = True

        if 'source' in configData:
            self.source = configData['source']
        else:
            self.source = "lqmt"
            self.logger.info("The 'source' parameter wasn't specified in your config. Defaulting to 'lqmt' to indicate"
                             "the data originated from lqmt.")

        if 'sourcetype' in configData:
            self.sourcetype = configData['sourcetype']
        else:
            raise ConfigurationError(
                "Missing the 'sourcetype' parameter in the Splunk tool named: {0}".format(self.getName())
            )
