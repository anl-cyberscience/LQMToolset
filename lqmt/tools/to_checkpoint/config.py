from datetime import datetime
import re
from subprocess import Popen, PIPE, STDOUT
from lqmt.lqm.tool import ToolConfig
import sys
import logging
from lqmt.lqm.config import ConfigurationError


class CheckpointConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self._logger = logging.getLogger("LQMT.Checkpoint.{0}".format(self.getName()))
        hasError = False

        if ('hostname' in configData):
            self._hostname = configData['hostname']
        else:
            self._logger.error("hostname must be specified in the configuration")
            hasError = True
        if ('port' in configData):
            self._port = configData['port']
        else:
            self._logger.error("port must be specified in the configuration")
            hasError = True
        if ('username' in configData):
            self._username = configData['username']
        else:
            self._logger.error("username must be specified in the configuration")
            hasError = True
        if ('originator' in configData):
            self._originator = configData['originator']
        else:
            self._logger.error("originator must be specified in the configuration")
            hasError = True
        if ('default_duration' in configData):
            self._defaultDuration = configData['default_duration']
        else:
            self._defaultDuration = 3 * 24 * 3600
            self._logger.warning(
                "default_duration not specified in the configuration, setting default_duration to 86400 seconds")

        if (hasError):
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_checkpoint tool")

    def _openCPCommand(self, cmd, inp=None):
        args = ["ssh", self._username + "@" + self._hostname]
        for arg in cmd:
            args.append(arg)
        p = Popen(args, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        return p

    def _copy_file(self, file):
        args = ["scp", file, self._username + "@" + self._hostname + ":" + file, ]
        p = Popen(args, stdout=PIPE, stderr=STDOUT, stdin=PIPE)
        eof = False
        while (p.returncode == None or not eof):
            line = p.stdout.readline()
            eof = not line
            if (not eof):
                line = line.decode(sys.stdout.encoding).strip()
                if (line != "This system is for authorized use only."):
                    self._logger.info(line)
            p.poll()

    def updateRules(self, blockIPs, unblockUIDs):
        eventID = datetime.now().strftime("%Y%m%d-%H%M%S")

        # write rules to file
        f = open('cp.txt', 'w')
        for ip in blockIPs:
            f.write("add -t " + str(
                ip._timeout) + " -a r -l r -o " + self._originator + " -c " + eventID + " ip -d " + ip._addr + "\n")
            f.write("add -t " + str(
                ip._timeout) + " -a d -l r -o " + self._originator + " -c " + eventID + " ip -s " + ip._addr + "\n")

        for uid in unblockUIDs:
            f.write("del " + uid + "\n")

        f.close()

        # copy file to checkpoint
        self._copy_file("cp.txt")
        # run command on checkpoint
        p = self._openCPCommand(["fw samp batch < cp.txt"])
        eof = False
        while (p.returncode == None or not eof):
            line = p.stdout.readline()
            eof = not line
            if (not eof):
                line = line.decode(sys.stdout.encoding).strip()
                if (line != "This system is for authorized use only."):
                    self._logger.info(line)
            p.poll()

    def getRules(self):
        self._logger.info("Retrieving current rules for originator '{0}'".format(self._originator))
        regexp = re.compile("originator=" + self._originator)
        p = self._openCPCommand(["fw samp get"])
        eof = False
        cout = p.stdout
        self._rules = {}
        lines = []
        nr = 0
        while (p.returncode == None or not eof):
            line = cout.readline()
            line = line.decode(sys.stdout.encoding)
            eof = not line
            if (not eof):
                match = regexp.search(line)
                if (match):
                    nr = nr + 1
                    rec = self._parseRule(line)
                    if ('dst_ip_addr' in rec):
                        ip = rec['dst_ip_addr']
                        if (not ip in self._rules):
                            self._rules[ip] = dict()
                        self._rules[ip]['out'] = rec
                    else:
                        ip = rec['src_ip_addr']
                        if (not ip in self._rules):
                            self._rules[ip] = dict()
                        self._rules[ip]['in'] = rec
                else:
                    lines.append(line)
            p.poll()
        if (p.returncode == 255):  # ssh failed
            self._logger.error("Error with ssh - disbaling")
            for line in lines:
                self._logger.error(line.strip())
            self.disable()
        else:
            self._logger.info("Retrieved {0} rules".format(nr))
        return self._rules

    def _parseRule(self, line):
        d = {}
        for x in line.strip().split(" "):
            k, v = x.split("=")
            d[k] = v
        return d

    def getDefaultDuration(self):
        return self._defaultDuration
