from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.config import ConfigurationError
import logging
import pan.xapi
import os.path
import sqlite3
from lxml import objectify
import ssl
import sys


class PaloAltoConfig(ToolConfig):
    def __init__(self, config, csvToolInfo, unhandledCSV):
        super().__init__(config, csvToolInfo, unhandledCSV)
        self._logger = logging.getLogger("LQMT.PaloAlto.{0}".format(self.getName()))
        hasError = False

        if ('api_key' in config):
            self._apiKey = config['api_key']
        else:
            self._apiKey = None
        if ('api_username' in config):
            self._userName = config['api_username']
        else:
            self._userName = None
        cur_version = sys.version_info
        if ('cafile' in config):
            if (cur_version < (3, 4)):
                self._logger.info("cafile specified, but not needed due to python version")
            self._cafile = config['cafile']
        else:
            if (cur_version >= (3, 4)):
                self._logger.error("cafile must be specified in the configuration")
                hasError = True
            self._cafile = None
        if ('api_password' in config):
            self._password = config['api_password']
        else:
            self._password = None
        if ('hostname' in config):
            self._hostname = config['hostname']
        else:
            self._logger.error("hostname must be specified in the configuration")
            hasError = True
        if ('badIPFiles' in config):
            self._badIPFiles = config['badIPFiles']
        else:
            self._logger.error("badIPFiles must be specified in the configuration")
            hasError = True
        if ('default_duration' in config):
            self._defaultDuration = config['default_duration']
        else:
            self._defaultDuration = 3 * 24 * 3600
            self._logger.warning(
                "default_duration not specified in the configuration, setting default_duration to 86400 seconds")
        if ('block_lists' in config):
            self._block_lists = config['block_lists']
        else:
            self._logger.error("block_lists must be specified in the configuration")
            hasError = True
        if (len(self._badIPFiles) != len(self._block_lists)):
            self._logger.error("The number of block list names and bad IP file MUST be the same")
            hasError = True

        if ('db_location' in config):
            self._db_location = config['db_location']
        else:
            self._db_location = "pa-{0}".format(self.getName())
            self._logger.info("db_location not specified using:  must be specified in the configuration")
            hasError = True
        if ('prune_method' in config):
            pm = config['prune_method']
            valid_emthods = ['Expiration', 'Added', 'Detected']
            if (pm in valid_emthods):
                self._prune_method = pm
            else:
                self._logger.error("Invalid prune method: {0}".format(pm))
        else:
            self._prune_method = 'Expiration'
        if (self._apiKey == None):
            if (self._userName == None or self._password == None):
                self._logger.error("Either the api_key or username/password must be specified in the configuration")
                hasError = True
        else:
            if (self._userName != None or self._password != None):
                self._logger.error(
                    "Only one of the api_key or username/password must be specified in the configuration")
                hasError = True
        if (hasError):
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_paloalto tool")
        ctx = None
        cur_version = sys.version_info
        if (cur_version >= (3, 4)):
            # required by pan api if python 3.4 is used
            ctx = ssl.create_default_context(cafile=self._cafile)
        self._xapi = pan.xapi.PanXapi(api_username=self._userName, api_password=self._password, api_key=self._apiKey,
                                      hostname=self._hostname, ssl_context=ctx)
        self._ipsPerBL = self._getIPsPerBL()
        self._ensureDBExists()

    def getDBConn(self):
        return self._conn

    def _ensureDBExists(self):
        dbfile = os.path.join(self._db_location, "{0}.db".format(self.getName()))
        if (not os.path.exists(self._db_location)):
            os.makedirs(self._db_location, 0o755, True)
        if (not os.path.exists(dbfile)):
            conn = sqlite3.connect(dbfile)
            c = conn.cursor()
            c.execute(
                "create table blocks (ip text primary key, detect_time integer(11), start_time integer(11), end_time integer(11), duration integer(11))")
            c.execute("create index detect_time on blocks(start_time)")
            c.execute("create index start_time on blocks(start_time)")
            c.execute("create index end_time on blocks(end_time)")
            conn.close()
        self._conn = sqlite3.connect(dbfile)

    def _getIPsPerBL(self):
        #        self._xapi.op("<show><system><state><filter>cfg.general.max-address</filter></state></system></show>")
        try:
            self._xapi.op("show system state filter \"cfg.general.max-address\"", cmd_xml=True)
            d = self._xapi.xml_root()
            o = objectify.fromstring(d)
            o.result
            s = o.result.text.split(" ")[1].strip();
            if (s.startswith("0x")):
                return int(s, 16) - 300
            else:
                return int(s) - 300
        except Exception as e:
            self._logger.error("Unable to retrieve max ip addresses")
            self._logger.error(str(e))
            self.disable()
            return 0

    def getXapi(self):
        return self._xapi

    def getBlockLists(self):
        return self._block_lists

    def getBlockFiles(self):
        return self._badIPFiles

    def getDefaultDuration(self):
        return self._defaultDuration

    def getMaxIPsToBlock(self):
        return self._ipsPerBL * len(self._badIPFiles)

    def getIPsPerFile(self):
        return self._ipsPerBL

    def getPruneMethod(self):
        return self._prune_method
