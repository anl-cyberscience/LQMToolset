import logging
import socket
from lqmt.lqm.data import AlertAction
from lqmt.lqm.logging import LQMLogging
from lqmt.lqm.tool import Tool


class ToSysLog(Tool):
    """ToSysLog communicates with the SysLog logger via udp or tcp based on the user config settings."""

    def __init__(self, config):
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))
        self._totalSent = 0
        self._messageHead = self._config.messageHead
        self._messageFields = self._config.messageFields

        if self.isEnabled():
            if self._config.protocol == 'tcp':
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self._socket.connect((self._config.host, self._config.port))
                except Exception as e:
                    self._logger.error(
                            "Unable to connect to remote Syslog server: {0}:{1}".format(self._config.host,
                                                                                        self._config.port))
                    self._logger.error(str(e))
                    self._socket = None
                    self.disable()
            else:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initialize(self):
        super().initialize()

    def process(self, data):
        """
        Process alerts to SysLog server. Message format defined in user config file

        :param data: alert data
        """

        if not self.isEnabled():
            return

        try:
            # format data being sent to syslog
            msg = self.format_syslog_msg(data.getFields(self._messageFields))
            syslog_msg = bytes("{0}\n".format(msg), 'UTF-8')
            if self._config.protocol == "TCP":
                self._socket.send(syslog_msg)
            else:
                self._socket.sendto(syslog_msg, (self._config.host, self._config.port))
            self._totalSent += 1
        except Exception as e:
            msg = "Error while sending data to remote Syslog server"
            if not LQMLogging.isDebug():
                self._logger.error(msg)
            else:
                self._logger.exception(msg)
            self._logger.error(str(e))

    def commit(self):
        pass

    def cleanup(self):
        self._logger.info("Send {0} messages to Syslog server".format(self._totalSent))
        if self.isEnabled():
            try:
                self._socket.close()
            except Exception as e:
                self._logger.error("Error while closing connection to remote Syslog server")
                self._logger.error(str(e))

    def format_syslog_msg(self, extractedfields):
        msg = self._messageHead
        step = 0  # used to iterate through extracted fields during format process

        # begin formatting...
        for i in self._messageFields:
            # extract value from extractedFields
            value = extractedfields[step]

            # check for existing quotes and strip
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            # append value to message
            msg += i + '="%s" ' % value
            step += 1
        return msg
