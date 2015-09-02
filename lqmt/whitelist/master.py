#from enum import Enum
import logging


class IndicatorTypes(object):
    """Enumeration of possible indicator types
    """
    ipv4='ipv4'
    ipv6='ipv6'
    ipv4subnet='ipv4wl'
    ipv6subnet='ipv6wl'
    domain='domain'
    host='host'
    url='url'

from .ipv4wl import IPv4WL
from .ipv6wl import IPv6WL
from .ipv4snwl import IPv4SubnetWL
from .ipv6snwl import IPv6SubnetWL
from .domainwl import DomainWL
from .hostwl import HostWL
from .urlwl import URLWL
import sys
import os
import hashlib

import sqlite3
sys.path.append('tpl/toml')
import toml

class MasterWhitelist(object):
    """The master whitelist object.
    This class is responsible for maintaining the database of all the whitelists
    and it is the central point for checking for whitelisted indicators
    """

    def __init__(self, configData=None, configFile=None):
        self._logger = logging.getLogger("LQMT.Whitelist")
        if(configData != None):
            self._loadConfig(configData)
        elif(configFile != None):
            self._loadConfigFromFile(configFile)

        self._updateDB()
        self._whitelists={}
        self._whitelists[IndicatorTypes.ipv4]=IPv4WL()
        self._whitelists[IndicatorTypes.ipv6]=IPv6WL()
        self._whitelists[IndicatorTypes.ipv4subnet]=IPv4SubnetWL()
        self._whitelists[IndicatorTypes.ipv6subnet]=IPv6SubnetWL()
        self._whitelists[IndicatorTypes.domain]=DomainWL()
        self._whitelists[IndicatorTypes.host]=HostWL()
        self._whitelists[IndicatorTypes.url]=URLWL()
        self._initMapping()
    
    def _initMapping(self):
        """Create the mapping of indicator types to the types of whitelists they will be checked against"""
        self._indicatorMapping={}
        self._indicatorMapping[IndicatorTypes.ipv4] = [IndicatorTypes.ipv4,IndicatorTypes.ipv4subnet]
        self._indicatorMapping[IndicatorTypes.ipv4subnet] = [IndicatorTypes.ipv4subnet]
        self._indicatorMapping[IndicatorTypes.ipv6] = [IndicatorTypes.ipv6,IndicatorTypes.ipv4subnet]
        self._indicatorMapping[IndicatorTypes.ipv6subnet] = [IndicatorTypes.ipv6subnet]
        self._indicatorMapping[IndicatorTypes.domain] = [IndicatorTypes.domain]
        self._indicatorMapping[IndicatorTypes.host] = [IndicatorTypes.host,IndicatorTypes.domain]
        self._indicatorMapping[IndicatorTypes.url] = [IndicatorTypes.url]
        
    def _loadConfigFromFile(self,configFile):
        cfg=open(configFile)
        config=toml.loads(cfg.read())
        cfg.close()
        self._loadConfig(config['Whitelist'])

    def _loadConfig(self,configData):
        self.db=configData['dbfile']
        self.whitelistFile=configData['whitelist']

    def _updateDB(self):
        """Update the DB"""
        if(not os.path.exists(self.db)):
            # Create it if not already there
            self._createDB()
        self.conn=sqlite3.connect(self.db)
        c=self.conn.cursor()
        # compute the md5 hash of the whitelist text file
        m = hashlib.md5()
        wlf=open(self.whitelistFile,"rb")
        m.update(wlf.read())
        md5=m.hexdigest()
        # and compare it against the md5 of the last file loaded
        c.execute("select md5 from md5")
        rec=c.fetchone()
        c.close()
        if(rec == None or rec[0] != md5):
            # if it is not the same, then reload the whitelist file
            self._reloadDB(md5)
        
    def _reloadDB(self,md5):
        whitelist=self ._loadWhitelistFile()
        DomainWL.storeDB(self.conn,whitelist['Domain'])
        HostWL.storeDB(self.conn,whitelist['Host'])
        IPv4WL.storeDB(self.conn,whitelist['IPv4Address'])
        IPv4SubnetWL.storeDB(self.conn,whitelist['IPv4Subnet'])
        IPv6WL.storeDB(self.conn,whitelist['IPv6Address'])
#        IPv6SubnetWL.storeDB(self.conn,whitelist['IPv6Subnet'])
        URLWL.storeDB(self.conn,whitelist['URL'])
        c=self.conn.cursor()
        c.execute("delete from md5")
        c.execute("insert into md5 values (?)" , (md5,))
        self.conn.commit()
        c.close()
        
        
    def _loadWhitelistFile(self):
        wlf=open(self.whitelistFile, "r")
        whitelist={}
        section=None
        for line in wlf.readlines():
            line=line.strip()
            if(len(line)> 0 and not line.startswith("#")):
                if(line.startswith("[")):
                    section=line[1:len(line)-1]
                    if(section not in whitelist):
                        whitelist[section]=[]
                else:
                    whitelist[section].append(line)
        wlf.close()
        return whitelist

    def _createDB(self):
        conn=sqlite3.connect(self.db)
        c=conn.cursor()
        c.execute("create table md5 (md5 text)")
        c.execute(IPv4WL.getCreateTable())
        c.execute(IPv6WL.getCreateTable())
        c.execute(IPv4SubnetWL.getCreateTable())
#        c.execute(IPv6SubnetWL.getCreateTable())
        c.execute(DomainWL.getCreateTable())
        c.execute(HostWL.getCreateTable())
        c.execute(URLWL.getCreateTable())
        c.close()
        conn.close()

    def isWhitelisted(self,indicatorType,indicator):
        """Return whether or not the specified indicator/indicatorType is whitelisted"""
        rv=False
        for wltype in self._indicatorMapping[indicatorType]:
            if(not rv):
                wl=self._whitelists[wltype]
                if(wl == None):
                    # Either throw an error or log a message
                    self._logger.error("Whitelist for type: {0} does not exist".format(wltype))
                    return False
                try:
                    rv=wl.isWhitelisted(self.conn,indicatorType,indicator)
                except Exception as e:
                    self._logger.error("Exception occurred while performing whitelist check")
                    self._logger.error(str(e))
        return rv
    