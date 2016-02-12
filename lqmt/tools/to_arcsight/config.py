from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.exceptions import ConfigurationError


class ArcSightConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        hasError = False

        if 'host' in configData:
            self._host = configData['host']
        else:
            self._logger.error("host must be specified in the configuration")
            hasError = True
        if 'port' in configData:
            self._port = configData['port']
        else:
            self._logger.error("port must be specified in the configuration")
            hasError = True
        if 'protocol' in configData:
            protocol = configData['protocol']
            if protocol == 'udp' or protocol == 'tcp':
                self._protocol = protocol
            else:
                self._logger.error("Invalid protocol: {0}".format(protocol))
                hasError = True
            self._protocol = configData['protocol']
        else:
            self._logger.error("protocol must be specified in the configuration")
            hasError = True

        if hasError:
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_arcsight tool")

    def getHost(self):
        return self._host

    def getPort(self):
        return self._port

    def getProtocol(self):
        return self._protocol
