'''
Created on Oct 23, 2014

@author: taxon
'''
import socket
from lqmt.lqm.tool import Tool
import logging
from lqmt.lqm.data import AlertAction
from lqmt.lqm.logging import LQMLogging


class ToArcSight(Tool):
    """ToArcSight communicates with the ArcSight logger via udp or tcp based on the configuration settings"""

    def __init__(self, config):
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ArcSight.{0}".format(self.getName()))
        self._totalSent = 0

        if self.isEnabled():
            # Open the appropriate type of socket
            if self._config.getProtocol() == 'tcp':
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self._socket.connect((config.getHost(), config.getPort()))
                except Exception as e:
                    self._logger.error(
                        "Unable to connect to ArcSight: {0}:{1}".format(config.getHost(), config.getPort()))
                    self._logger.error(str(e))
                    self._socket = None
                    self.disable()
            else:
                self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initialize(self):
        super().initialize()

    def process(self, data):
        """Pass the alert to the ArcSight Logger instance.  data is a CEF string."""
        if not self.isEnabled():
            return
        s = data.toCEFString()
        try:
            msg = bytes("{0}\n".format(s), 'UTF-8')
            if self._config.getProtocol() == 'tcp':
                self._socket.send(msg)
            else:
                self._socket.sendto(msg, (self._config.getHost(), self._config.getPort()))
            self._totalSent += 1
        except Exception as e:
            msg = "Error while sending data to ArcSight server"
            if not LQMLogging.isDebug():
                self._logger.error(msg)
            else:
                self._logger.exception(msg)
            self._logger.error(str(e))

    def commit(self):
        pass

    def cleanup(self):
        self._logger.info("Sent {0} messages to ArcSight server".format(self._totalSent))
        if self.isEnabled():
            try:
                self._socket.close()
            except Exception as e:
                self._logger.error("Error while closing connection to ArcSight server")
                self._logger.error(str(e))
