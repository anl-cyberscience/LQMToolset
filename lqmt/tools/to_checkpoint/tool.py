from lqmt.lqm.tool import Tool
import logging
from lqmt.lqm.data import AlertAction


class Block():
    def __init__(self, ip, timeout):
        self._addr = ip
        self._timeout = timeout


class ToCheckpoint(Tool):
    originator = "CFM"

    def __init__(self, config):
        super().__init__(config, [AlertAction.get('Block'), AlertAction.get('Revoke')])
        self._logger = logging.getLogger("LQMT.Checkpoint.{0}".format(self.getName()))
        self._rules = {}  # CFM-created rules from config device
        self._blocks = set()  # Blocks to block that aren't already blocked
        self._blockIPs = set()
        self._unblockUIDs = set()  # IPs to unblock
        self._totalProcessed = 0
        self._totalBlocked = 0
        self._totalRevoked = 0
        self._modified = False
        self._cp = config

    def initialize(self):
        super().initialize()
        self._rules = self._cp.getRules()

    def process(self, alert):
        self._totalProcessed += 1
        action = alert.getAction()
        if action == AlertAction.get('Block'):
            self._block(alert)
        elif action == AlertAction.get('Revoke'):
            self._revoke(alert)

    def commit(self):
        # Possibly look for the refresh process before writing file?
        self._logger.info("Updating checkpoint")
        self._cp.updateRules(self._blocks, self._unblockUIDs)

    def cleanup(self):
        self._logger.info(
                "Processed {0} alerts.  New blocks: {1}  New revoke: {2}".format(self._totalProcessed,
                                                                                 self._totalBlocked,
                                                                                 self._totalRevoked))

    def _block(self, alert):
        addr = alert.getIPToBlock()
        if addr is None:
            self.unprocessed(alert)
            return
        if self.is_valid_ipv4(addr) or self.is_valid_ipv6(addr):
            if addr not in self._rules and addr not in self._blockIPs:
                self._blocks.add(Block(addr, self._getDuration(alert)))
                self._blockIPs.add(addr)
                self._totalBlocked += 1
                self._modified = True
                return True
        return False

    def _getDuration(self, alert):
        duration = alert.getDuration1()
        if duration is None or int(duration) == 0:
            return self._config.getDefaultDuration()
        return duration

    def _revoke(self, alert):
        addr = alert.getIPToBlock()
        if addr is None:
            self.unprocessed(alert)
            return
        if self.is_valid_ipv4(addr) or self.is_valid_ipv6(addr):
            if addr in self._rules:
                self._unblockUIDs.add(self._rules[addr]['in']['uid'])
                self._unblockUIDs.add(self._rules[addr]['out']['uid'])
                self._totalRevoked += 1
                self._modified = True
                return True
        return False

    def unblockAll(self):
        self.loadDeviceConfig()
        for addr in self._rules:
            if 'in' not in self._rules[addr]:
                self._logger.info(("No inbound block for addr= %s" % addr))
            else:
                self._unblockUIDs.add(self._rules[addr]['in']['uid'])
            if 'out' not in self._rules[addr]:
                self._logger.info(("No outbound block for addr= %s" % addr))
            else:
                self._unblockUIDs.add(self._rules[addr]['out']['uid'])
        self.commit()
