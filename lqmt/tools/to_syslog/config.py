import logging
from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.exceptions import ConfigurationError


class SysLogConfig(ToolConfig):
    """
       ToSyslog config variables:
        * = required
        *host - address of remote syslog address
        port - port that remote syslog server is listening on(defaults to 514)
        *protocol - protocol you want to communicate with(tcp/udp)
        *messageHead - Define what you want to have at the beginning of every message sent to syslog
        *messageFields - specify what fields you want extracted from the alerts and included in the messages
            note: Selected fields will be appended to end of message as so:
            ex: *messageHead* indicatorType="IPV4" indicator="192.168.1.1"
    """
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))

        self.host = self.validation('host', str, required=True)
        self.port = self.validation('port', int, default=514)
        self.protocol = self.validation('protocol', str, default="tcp")
        self.messageHead = self.validation('messageHead', str, required=True)
        self.messageFields = self.validation('messageFields', list, required=True)

        # Additional checks
        if self.protocol.lower() not in ['tcp', 'udp']:
            raise ConfigurationError("The provided value for the variable configuration variable 'protocol' is "
                                     "invalid. Value provided: {0} Valid values: 'tcp', 'udp".format(self.protocol))
