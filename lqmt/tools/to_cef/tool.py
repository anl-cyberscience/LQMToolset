import socket
from lqmt.lqm.tool import Tool
from datetime import datetime
import re
import logging
from lqmt.lqm.data import AlertAction


class Header():
    """CEF Header object - contains the fields needed to create the CEF header"""

    def __init__(self, alert):
        # necessary escapes
        self._replacer = multiple_replacer(('|', '\|'), ('\\', '\\\\'))
        self._version = 0
        self._deviceVendor = "DOECFM"
        self._deviceProduct = "ToCEF"
        self._deviceVersion = "1.0.1"
        self._signatureID = alert.getReason()
        self._name = alert.getReason()
        self._severity = 5
        self._timestamp = alert.getProcessedTime()


    def toCEFString(self):
        """Outout the header as a properly formatted CEF header."""
        ts = datetime.fromtimestamp(int(self._timestamp))
        s = ts.strftime("%b %d %H:%M:%S")
        s += " " + socket.gethostname()
        s += " CEF:{0}|{1}|{2}|{3}|{4}|{5}|{6}".format(self._version, self._escape(self._deviceVendor),
                                                       self._escape(self._deviceProduct),
                                                       self._escape(self._deviceVersion),
                                                       self._escape(self._signatureID), self._escape(self._name),
                                                       self._severity)
        return s

    def _escape(self, s):
        return self._replacer(s)


class Record():
    def _toDate(self, unixtime):
        if (unixtime == None):
            return None
        ts = datetime.fromtimestamp(int(unixtime))
        return ts.strftime("%b %d %Y %H:%M:%S")

    def __init__(self, alert):
        self._alert = alert
        self._replacer = multiple_replacer(('=', '\\='), ('\\', '\\\\'), ('\r\n', '\\n'), ('\n', '\\n'), ('\r', '\\n'))
        self._initFields()
        self._header = Header(alert)
        self._externalID = alert.getDataItemID()
        self._start = self._toDate(alert.getDetectedTime())
        self._rt = self._toDate(alert.getProcessedTime())
        self._src = alert.getSourceIP()
        self._dst = alert.getDestIP()
        self._request = alert.getURL()
        self._shost = alert.getSourceHost()
        self._dhost = alert.getDestHost()
        self._spt = alert.getSourcePort()
        self._dpt = alert.getDestPort()
        self._proto = alert.getTransportProtocol()
        self._deviceExternalID = alert.getDirectSource()
        self._act = alert.getAction()
        self._end = self._toDate(alert.getEndTime())
        self._cat = alert.getReason()
        self._priors = alert.getPriors()
        self._msg = alert.getComment()
        self._extensions = dict()
        self._extensions['Restrictions'] = alert.getRestriction()
        self._extensions['Sensitivity'] = alert.getSensitivity()
        self._extensions['ReconAllowed'] = alert.getReconAllowed()
        self._extensions['FileID'] = alert.getFileID()
        self._extensions['ReportedTime'] = self._toDate(alert.getReportedTime())
        self._extensions['SecondarySource'] = alert.getSecondarySource()
        self._extensions['Confidence'] = alert.getConfidence()
        self._extensions['Severity'] = alert.getSeverity()
        self._extensions['Relevance'] = alert.getRelevance()
        self._extensions['RelatedID'] = alert.getRelatedID()
        self._extensions['RelationType'] = alert.getRelationType()
        self._extensions['FileHasMore'] = alert.getFileHasMore()

    def _initFields(self):
        self._fields = []
        self._fields.append('externalID')
        self._fields.append('start')
        self._fields.append('rt')
        self._fields.append('src')
        self._fields.append('dst')
        self._fields.append('request')
        self._fields.append('shost')
        self._fields.append('dhost')
        self._fields.append('spt')
        self._fields.append('dpt')
        self._fields.append('proto')
        self._fields.append('deviceExternalID')
        self._fields.append('act')
        self._fields.append('end')
        self._fields.append('cat')
        self._fields.append('priors')
        self._fields.append('msg')

    def toCEFString(self):
        """Create the CEF string.  Only include fields that aren't None"""
        s = self._header.toCEFString()
        sep = "|"
        for ofld in self._fields:
            fld = "_" + ofld
            if hasattr(self, fld):
                val = getattr(self, fld)
                if val != None:
                    s += sep + self._escape(ofld) + "=" + self._escape(val)
                    sep = " "
        for fld, val in self._extensions.items():
            if val is not None:
                s += sep + self._escape(fld) + "=" + self._escape(val)
                sep = " "
        return s

    def _escape(self, s):
        return self._replacer(s)


class ToCEF(Tool):
    def __init__(self, config):
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.CEF.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def process(self, data):
        try:
            return Record(data)
        except Exception as e:
            self._logger.error("Error occurred in creating CEF data")
            self._logger.error(str(e))

    def commit(self):
        pass

    def cleanup(self):
        pass


def multiple_replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)


def multiple_replace(string, *key_values):
    return multiple_replacer(*key_values)(string)
