from lqmt.lqm.tool import Tool
import logging
import pan.xapi
import time
import datetime
from lqmt.lqm.data import AlertAction

class Block:
    """Class to hold information on blocks/revokes"""

    def __init__(self,ip,detected,duration):
        self._ip=ip
        self._detected=int(detected)
        if(duration != None):
            self._duration=int(duration)
        else:
            self._duration=None
    def getAddr(self):
        return self._ip

    def getDetectedTime(self):
        return self._detected

    def setDetectedTime(self, dt):
        self._detected=dt

    def getDuration(self):
        return self._duration

class ToPaloAlto(Tool):
    '''
    '''

    def __init__(self, config):
        super().__init__(config, [AlertAction.get('Block'), AlertAction.get('Revoke')])

        # self._config=config
        self._conn = self._config.getDBConn()
        self._cur = self._conn.cursor()
        self._xapi=self._config.getXapi()
        self._totalProcessed=0
        self._totalBlocked=0
        self._totalRevoked=0
        self._totalUpdated=0
        self._totalPruned=0
        self._totalExpired=0
        self._logger = logging.getLogger("LQMT.PaloAlto.{0}".format(self.getName()))
        self._blocks=dict()
        self._revokes=dict()
        # max per query controls the number of ips per query that are handled.  This is done to ensure that sqlite
        # and python don't have issues if there a significant number of ips to process at once 
        self._maxPerQuery=100

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """Process an alert."""
        self._totalProcessed=self._totalProcessed+1;
        action=alert.getAction()
        if(action == AlertAction.get('Block')):
            self._block(alert)
        elif (action==AlertAction.get('Revoke')):
            self._revoke(alert)

    def commit(self):
        """Commit the changes to the device."""
        # update the database with the new blocks/revokes
        self._updateDB()
        # write the blocks to the EBL files
        self._writeBlocks(self._config.getBlockFiles())
        for ebl in self._config.getBlockLists():
            # tell the device to refresh teach EBL
            try:
                self._xapi.op("request system external-list refresh name \"{0}\"".format(ebl),cmd_xml=True)
            except pan.xapi.PanXapiError as exc:
                self._logger.error("Unable to refresh EBL: {0}".format(ebl))
                self._logger.error(str(exc))

    def cleanup(self):
        self._logger.info("Processed {0} alerts.  New blocks: {1}  Updated Blocks: {2} New revoke: {3} Expired: {4} Pruned: {5}".format(self._totalProcessed,self._totalBlocked,self._totalUpdated,self._totalRevoked,self._totalExpired,self._totalPruned))

    def _updateDB(self):
        """Update the database  - remove any revoked IPs, add any new blocks, and prune if necessary"""
        bk=self._blocks.keys()
        rk=self._revokes.keys()
        allAddrs=set(bk)
        allAddrs.update(rk)
        for addr in allAddrs:
            if(addr in bk and addr in rk):
                # this address appears in both blocks and revokes - use the most recently detected
                b=self._blocks[addr]
                r=self._revokes[addr]
                if(b.getDetectedTime() > r.getDetectedTime()):
                    del self._revokes[addr]
                else:
                    del self._blocks[addr]
        # remove any revoked ips from the database
        if(len(self._revokes) > 0):
            todel=[]
            for r in self._revokes.values():
                todel.append(r.getAddr())
            self._totalRevoked=self._deleteIPsFromDB(todel)
        else:
            self._totalRevoked=0
        ctime=int(time.time())
        blocks=0
        if(len(self._blocks) > 0):
            # if there are blocks,
            # first remove any IPs that already are in the DB (so there are no duplicates)
            # this doesn't currently check to see if an existing block would expire later than a new one 
            # or if the one already in the database was detected before the one about to be added.
            todel=[]
            for b in self._blocks.values():
                todel.append(b.getAddr())
            self._totalUpdated=self._deleteIPsFromDB(todel)

            toadd=list(self._blocks.values())
            # Add the IPs to the DB in _maxPerQuery-sized chunks.
            while(toadd):
                thisadd=toadd[:self._maxPerQuery]
                del toadd[:self._maxPerQuery]
                parms=[]
                for b in thisadd:
                    # if the end time is None, then it is an infinite block and will not be removed until
                    # it is either revoked or removed due to pruning because there are more IPs than the device can handle
                    dur=b.getDuration()
                    if(dur==None):
                        endTime=None
                    else:
                        endTime=ctime+dur
                    parms.append( (b.getAddr(),b.getDetectedTime(),ctime,dur,endTime) )
                self._cur.executemany("insert into blocks (ip,detect_time,start_time,duration,end_time) values (?,?,?,?,?)", parms)
                blocks=blocks+self._cur.rowcount
                self._conn.commit()
        self._totalBlocked=blocks-self._totalUpdated

        # now remove any that have expired
        self._cur.execute("delete from blocks where end_time < ?",(ctime,))
        self._conn.commit()
        self._totalExpired=self._cur.rowcount

        # now that the DB is updated, check to see if it needs to be pruned
        nr=self._getNumRecs()
        toPrune=nr - self._config.getMaxIPsToBlock()
        if(toPrune>0):
            pm=self._config.getPruneMethod()
            # got some pruning to do
            if(pm=='Expiration'):
                self._pruneByExpiration(toPrune,ctime)
            elif (pm=='Added'):
                self._pruneByTimeAdded(toPrune,ctime)
            elif (pm=='Detected'):
                self._pruneByTimeDetected(toPrune,ctime)
        if(toPrune-self._totalPruned > 0):
            #still have more to prune, so use time added as a fall-back
            self._logger.info("Primary pruning method did not remove enough.  Using TimeAdded to prune more")
            tp=self._totalPruned
            self._pruneByTimeAdded(toPrune-self._totalPruned,ctime)
            self._totalPruned=self._totalPruned+tp

    def _deleteIPsFromDB(self,todel):
        """Delete the ips specified in todel from the database."""
        cnt=0
        #self._maxPerQuery limits the number of items in one deletion as a safeguard against a very large query
        while(todel):
            thisdel=todel[:self._maxPerQuery]
            del todel[:self._maxPerQuery]
            self._cur.execute("delete from blocks where ip in ('{0}')".format("','".join(thisdel)))
            self._conn.commit()
            cnt=cnt+self._cur.rowcount
        return cnt

    def _pruneByExpiration(self,toPrune,ctime):
            # delete blocks starting from the soonest to expire until we have reached the limit
            todel=[]
            self._logger.warning("Pruning {0} blocks by expiration:".format(toPrune))
            for r in self._cur.execute("select ip,end_time from blocks where end_time is not null order by end_time limit {0}".format(toPrune)):
                todel.append(r[0])
                expire=datetime.datetime.fromtimestamp(r[1]).strftime("%c")
                self._logger.warning("ip: {0} expiration: {1}: {2} seconds early".format(r[0],expire,r[1]-ctime))
            self._totalPruned=self._deleteIPsFromDB(todel)

    def _pruneByTimeAdded(self,toPrune):
            # delete blocks starting from the least recently added until we have reached the limit
            todel=[]
            for r in self._cur.execute("select ip,start_time,end_time from blocks order by start_time limit {0}".format(toPrune)):
                todel.append(r[0])
                self._logger.warning("Prune: removing block before expiration for ip: {0} expiration: {1}".format(r[0],r[1]))
            self._totalPruned=self._deleteIPsFromDB(todel)

    def _pruneByTimeDetected(self,toPrune):
            # delete blocks starting from the least recently detected until we have reached the limit
            todel=[]
            for r in self._cur.execute("select ip,detect_time,end_time from blocks order by detect_time limit {0}".format(toPrune)):
                todel.append(r[0])
                self._logger.warning("Prune: removing block before expiration for ip: {0} expiration: {1}".format(r[0],r[1]))
            self._totalPruned=self._deleteIPsFromDB(todel)

    def _getNumRecs(self):
        """Return the number of records in the database"""
        self._cur.execute("select count(*) as num from blocks")
        r=self._cur.fetchone()
        return r[0]

    def _revoke(self,alert):
        """Revoke the block of the IP specified in the alert."""
        addr=alert.getIPToBlock()
        if(addr == None):
            # this alert will be unprocessed - put it in the unprocessed file
            self.unprocessed(alert)
            return
        if(self.is_valid_ipv4(addr) or self.is_valid_ipv6(addr)):
            if (addr in self._blocks.keys()):
                r=self._revokes[addr]
                # if tyis is a newer revoke than one already in the list
                if(alert.getDetectedTime() > r.getDetectedTime() ):
                    # update the detected time
                    r.setDetectedTime(alert.getDetectedTime())
            else:
                #otherwise just add it to the revoke list
                self._revokes[addr]=Block(addr,alert.getDetectedTime(),None)
            return True
        return False

    def _block(self,alert):
        """Block the ip from the alert for the duration specified in the alert."""
        addr=alert.getIPToBlock()
        if(addr == None):
            # this alert will be unprocessed - put it in the unprocessed file
            self.unprocessed(alert)
            return
        if(self.is_valid_ipv4(addr) or self.is_valid_ipv6(addr)):
            if (addr in self._blocks.keys()):
                # is this a newer block than we have seen during this round of processing?
                b=self._blocks[addr]
                if(int(alert.getDetectedTime()) > b.getDetectedTime() ):
                    # if so, update the detected time and duration
                    b.setDetectedTime(alert.getDetectedTime())
                    b.setDuration(self._getDuration(alert))
            else:
                #otherwise add it to the blocks list
                self._blocks[addr]=Block(addr,alert.getDetectedTime(),self._getDuration(alert))
            return True
        return False

    def _getDuration(self, alert):
        """Return duration.  If the duration is 0, that means infintite.  If it is None, then use the default duration"""
        duration=alert.getDuration1()
        if(duration==None):
            return self._config.getDefaultDuration()
        if(int(duration)==0):
            return None
        return duration

    def _writeBlocks(self,ipFiles):
        """Write the blocked IPs to the files.  At this point, the database should have no more than can be handled by the device."""
        ipsPerFile=self._config.getIPsPerFile()
        blockFiles=self._config.getBlockFiles()
        curFileIdx=0
        f=None
        n=0
        # retrieve the blocked ips from the database
        for r in self._cur.execute("select ip from blocks order by ip"):
            #strat a new file if necessary
            if(n>=ipsPerFile or f==None):
                if(f!=None):
                    f.close()
                    curFileIdx=curFileIdx+1
                f=open(blockFiles[curFileIdx],"w")
                n=0
            f.write(r[0]+"\n")
            n=n+1
        if(f!=None):
            f.close()
            curFileIdx=curFileIdx+1

        # The palo alto Dynamic Block Lists mechanism doesn't like non-existent or empty EBL files, so make sure there is a "dummy" ip in all that would be empty
        for fn in blockFiles[curFileIdx:]:
            # the PA will have issues with a file with no entries, so write a single VALID ip
            f=open(fn,"w")
            f.write("131.131.131.131\n")
            f.close()

    def fileBegin(self):
        # No special processing when a new file is started
        pass

    def fileDone(self):
        # No special processing when a file is done
        pass
