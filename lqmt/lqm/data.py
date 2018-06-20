from lqmt.whitelist.master import IndicatorTypes


class AlertAction(object):
    """Enum of all possible actions"""
    enums = ["All", "Block", "Notify", "Watch", "SendReport", "Revoke", "Query", "OtherAction"]

    @staticmethod
    def get(action):
        if action in AlertAction.enums:
            return action
        raise Exception("Invalid action specified: {0}".format(action))


class AlertFields(object):
    """Class to aid in properly formatting fields as strings and checking for existence of alert fields"""

    def __init__(self):
        self._fields = {"dataItemID": "S", "fileID": "S", "detectedTime": "I", "reportedTime": "I",
                        "processedTime": "I", "indicator": "S", "indicatorType": "S", "indicatorDirection": "S",
                        "secondaryIndicator": "S", "secondaryIndicatorType": "S", "secondaryIndicatorDirection": "S",
                        "directSource": "S", "secondarySource": "S", "action1": "S", "duration1": "I", "action2": "S",
                        "duration2": "I", "reason1": "S", "reference1": "S", "reason2": "S", "reference2": "S",
                        "majorTags": "S", "minorTags": "S", "restriction": "S", "sensitivity": "S", "reconAllowed": "S",
                        "priors": "I", "confidence": "I", "severity": "I", "relevancy": "I", "relatedID": "S",
                        "relationType": "S", "comment": "S", "fileHasMore": "I"
                        }

    def isValid(self, field):
        return field in self._fields

    def getStringRepresentation(self, field, val):
        """Return a string representation of the specified field"""
        if not self.isValid(field):
            raise Exception("Alert field {0} is not a valid field".format(field))
        ftype = self._fields[field]
        if ftype == "I":
            if val is not None:
                return val
            else:
                return ""
        elif ftype == "S":
            if val is not None:
                return '"' + val + '"'
            else:
                return ""
        elif ftype == "E":
            if val is not None:
                return '"' + val.name + '"'
            else:
                return ""

    @property
    def fields(self):
        return self._fields


class Alert(object):
    """The Alert object represents the LQM intermediate format"""
    _alertFields = AlertFields()

    @staticmethod
    def isValidField(field):
        return Alert._alertFields.isValid(field)

    def __init__(self):
        self._dataItemID = None
        self._fileID = None
        self._detectedTime = None
        self._reportedTime = None
        self._processedTime = None
        self._indicator = None
        self._indicatorType = None
        self._indicatorDirection = None
        self._secondaryIndicator = None
        self._secondaryIndicatorType = None
        self._secondaryIndicatorDirection = None
        self._directSource = None
        self._secondarySource = None
        self._action1 = None
        self._duration1 = None
        self._action2 = None
        self._duration2 = None
        self._reason1 = None
        self._reference1 = None
        self._reason2 = None
        self._reference2 = None
        self._majorTags = None
        self._minorTags = None
        self._restriction = None
        self._sensitivity = None
        self._reconAllowed = None
        self._priors = None
        self._confidence = None
        self._severity = None
        self._relevancy = None
        self._relatedID = None
        self._relationType = None
        self._comment = None
        self._fileHasMore = None

    # setters
    def setFromDict(self, d):
        """Set the fields from the dictionary"""
        if 'dataItemID' in d:
            self._dataItemID = d['dataItemID']
        if 'fileID' in d:
            self._fileID = d['fileID']
        if 'detectedTime' in d:
            self._detectedTime = d['detectedTime']
        if 'reportedTime' in d:
            self._reportedTime = d['reportedTime']
        if 'processedTime' in d:
            self._processedTime = d['processedTime']
        if 'indicator' in d:
            self._indicator = d['indicator']
        if 'indicatorType' in d:
            self._indicatorType = d['indicatorType']
            if self._indicatorType == "URL":
                pass
        if 'indicatorDirection' in d:
            self._indicatorDirection = d['indicatorDirection']
        if 'secondaryIndicator' in d:
            self._secondaryIndicator = d['secondaryIndicator']
        if 'secondaryIndicatorType' in d:
            self._secondaryIndicatorType = d['secondaryIndicatorType']
        if 'secondaryIndicatorDirection' in d:
            self._secondaryIndicatorDirection = d['secondaryIndicatorDirection']
        if 'directSource' in d:
            self._directSource = d['directSource']
        if 'secondarySource' in d:
            self._secondarySource = d['secondarySource']
        if 'action1' in d:
            self._action1 = AlertAction.get(d['action1'])
        if 'duration1' in d:
            self._duration1 = d['duration1']
        if 'action2' in d:
            self._action2 = AlertAction.get(d['action2'])
        if 'duration2' in d:
            self._duration2 = d['duration2']
        if 'reason1' in d:
            self._reason1 = d['reason1']
        if 'reference1' in d:
            self._reference1 = d['reference1']
        if 'reason2' in d:
            self._reason2 = d['reason2']
        if 'reference2' in d:
            self._reference2 = d['reference2']
        if 'majorTags' in d:
            self._majorTags = d['majorTags']
        if 'minorTags' in d:
            self._minorTags = d['minorTags']
        if 'restriction' in d:
            self._restriction = d['restriction']
        if 'sensitivity' in d:
            self._sensitivity = d['sensitivity']
        if 'reconAllowed' in d:
            self._reconAllowed = d['reconAllowed']
        if 'priors' in d:
            self._priors = d['priors']
        if 'confidence' in d:
            self._confidence = d['confidence']
        if 'severity' in d:
            self._severity = d['severity']
        if 'relevancy' in d:
            self._relevancy = d['relevancy']
        if 'relatedID' in d:
            self._relatedID = d['relatedID']
        if 'relationType' in d:
            self._relationType = d['relationType']
        if 'comment' in d:
            self._comment = d['comment']
        if 'fileHasMore' in d:
            self._fileHasMore = d['fileHasMore']

    def isWhitelisted(self, wl):
        """Return whether or not this Alert is whitelisted"""
        if wl is None:
            return False
        # check both primary and secondary indicators (if they exist)
        if self._indicator is not None:
            if wl.isWhitelisted(self._getIndicatorType(self._indicatorType), self._indicator):
                return True
        if self._secondaryIndicator is not None:
            if wl.isWhitelisted(self._getIndicatorType(self._secondaryIndicatorType), self._secondaryIndicator):
                return True
        return False

    @staticmethod
    def _getIndicatorType(indType):
        """Return the enumerated indicator type of the indType"""
        if indType == "IPv4Address":
            return IndicatorTypes.ipv4
        elif indType == "IPv6Address":
            return IndicatorTypes.ipv6
        elif indType == "DNSDomainName":
            return IndicatorTypes.domain
        elif indType == "DNSHostName":
            return IndicatorTypes.host
        elif indType == "URL":
            return IndicatorTypes.url

    def setDataItemID(self, dataItemID):
        self._dataItemID = dataItemID

    def setFileID(self, fileID):
        self._fileID = fileID

    def setDetectedTime(self, detectedTime):
        self._detectedTime = detectedTime

    def setReportedTime(self, reportedTime):
        self._reportedTime = reportedTime

    def setProcessedTime(self, processedTime):
        self._processedTime = processedTime

    def setIndicator(self, indicator):
        self._indicator = indicator

    def setIndicatorType(self, indicatorType):
        self._indicatorType = indicatorType

    def setIndicatorDirection(self, indicatorDirection):
        self._indicatorDirection = indicatorDirection

    def setSecondaryIndicator(self, secondaryIndicator):
        self._secondaryIndicator = secondaryIndicator

    def setSecondaryIndicatorType(self, secondaryIndicatorType):
        self._secondaryIndicatorType = secondaryIndicatorType

    def setSecondaryIndicatorDirection(self, secondaryIndicatorDirection):
        self._secondaryIndicatorDirection = secondaryIndicatorDirection

    def setDirectSource(self, directSource):
        self._directSource = directSource

    def setSecondarySource(self, secondarySource):
        self._secondarySource = secondarySource

    def setAction1(self, action1):
        self._action1 = action1

    def setDuration1(self, duration1):
        self._duration1 = duration1

    def setAction2(self, action2):
        self._action2 = action2

    def setDuration2(self, duration2):
        self._duration2 = duration2

    def setReason1(self, reason1):
        self._reason1 = reason1

    def setReference1(self, reference1):
        self._reference1 = reference1

    def setReason2(self, reason2):
        self._reason2 = reason2

    def setReference2(self, reference2):
        self._reference2 = reference2

    def setMajorTags(self, majorTags):
        self._majorTags = majorTags

    def setMinorTags(self, minorTags):
        self._minorTags = minorTags

    def setRestriction(self, restriction):
        self._restriction = restriction

    def setSensitivity(self, sensitivity):
        self._sensitivity = sensitivity

    def setReconAllowed(self, reconAllowed):
        self._reconAllowed = reconAllowed

    def setPriors(self, priors):
        self._priors = priors

    def setConfidence(self, confidence):
        self._confidence = confidence

    def setSeverity(self, severity):
        self._severity = severity

    def setRelevancy(self, relevancy):
        self._relevancy = relevancy

    def setRelatedID(self, relatedID):
        self._relatedID = relatedID

    def setRelationType(self, relationType):
        self._relationType = relationType

    def setComment(self, comment):
        self._comment = comment

    def setFileHasMore(self, fileHasMore):
        self._fileHasMore = fileHasMore

    # getters
    def getDataItemID(self):
        return self._dataItemID

    def getDetectedTime(self):
        return self._detectedTime

    def getProcessedTime(self):
        return self._processedTime

    def getDuration1(self):
        return self._duration1

    def getIPToBlock(self):
        if self.getAction() == AlertAction.get('Block') and self._indicatorType == "IPv4Address":
            return self._indicator
        else:
            return None

    def getIPToRevoke(self):
        if self.getAction() == AlertAction.get('Revoke') and self._indicatorType != "IPv4Address":
            return self._indicator
        else:
            return None

    def getSourceIP(self):
        if self._indicatorDirection is None or self._indicatorDirection == "destination":
            return None
        if self._indicatorType is None:
            return None
        if self._indicatorType != "IPv4Address":
            return None
        return self._indicator

    def getDestIP(self):
        if self._indicatorDirection is None or self._indicatorDirection == "source":
            return None
        if self._indicatorType is None:
            return None
        if self._indicatorType != "IPv4Address":
            return None
        return self._indicator

    def getURL(self):
        if self._indicatorType != "URL":
            return None
        return self._indicator

    def getSourceHost(self):
        if self._indicatorDirection is None or self._indicatorDirection == "destination":
            return None
        if self._indicatorType is None:
            return None
        if self._indicatorType != "DNSHostName":
            return None
        return self._indicator

    def getDestHost(self):
        if self._indicatorDirection is None or self._indicatorDirection == "source":
            return None
        if self._indicatorType is None:
            return None
        if self._indicatorType != "DNSHostName":
            return None
        return self._indicator

    def getSourcePort(self):
        # parser currently doesn't support secondaryIndicators
        if self._secondaryIndicatorDirection is None or self._secondaryIndicatorDirection == "destination":
            return None
        if self._secondaryIndicatorType is None:
            return None
        if self._secondaryIndicatorType != "tcpport" or self._secondaryIndicatorType != "udpport":
            return None
        return self._secondaryIndicator

    def getDestPort(self):
        # parser currently doesn't support secondaryIndicators
        if self._secondaryIndicatorDirection is None or self._secondaryIndicatorDirection == "source":
            return None
        if self._secondaryIndicatorType is None:
            return None
        if self._secondaryIndicatorType != "tcpport" or self._secondaryIndicatorType != "udpport":
            return None
        return self._secondaryIndicator

    def getTransportProtocol(self):
        # parser currently doesn't support secondaryIndicators
        if self._secondaryIndicatorDirection is None or self._secondaryIndicatorDirection == "destination":
            return None
        if self._secondaryIndicatorType is None:
            return None
        if self._secondaryIndicatorType == "tcpport":
            return "TCP"
        else:
            return "UDP"

    def getDirectSource(self):
        return self._directSource

    def getAction(self):
        return self._action1

    def getEndTime(self):
        # this could be processedTime + duration or reportedTime + duration or detectedTime + duration
        #  for now use none of those
        return None

    def getReason(self):
        return self._reason1

    def getPriors(self):
        return self._priors

    def getComment(self):
        return self._comment

    def getRestriction(self):
        return self._restriction

    def getSensitivity(self):
        return self._sensitivity

    def getReconAllowed(self):
        return self._reconAllowed

    def getFileID(self):
        return self._fileID

    def getReportedTime(self):
        return self._reportedTime

    def getSecondarySource(self):
        return self._secondarySource

    def getConfidence(self):
        return self._confidence

    def getSeverity(self):
        return self._severity

    def getRelevance(self):
        return self._relevancy

    def getRelatedID(self):
        return self._relatedID

    def getRelationType(self):
        return self._relationType

    def getFileHasMore(self):
        return self._fileHasMore

    def getFields(self, fieldNames):
        fields = []
        for field in fieldNames:
            fields.append(Alert._alertFields.getStringRepresentation(field, self._getField(field)))
        return fields

    def _getField(self, field):
        val = None
        tfld = "_" + field
        if hasattr(self, tfld):
            val = getattr(self, tfld)
        return val

    def getAllFields(self, dictionary=False, parseEmpty=False, emptyValue=None):
        """
        Method to get all supported fields from the intermediate data format.
        :param dictionary: Option to return the results as a dictionary. Defaults to False.
        :param parseEmpty: Option to parse out any empty values.
        :param emptyValue: Option to fill in empty fields with a different value
        :return: Returns either a list or dictionary of all fields and their parsed value. Defaults to a list.
        """
        keys = list(Alert._alertFields.fields.keys())
        fields = self.getFields(keys)
        if dictionary:
            dict_fields = {}
            keys.reverse()
            for value in fields:
                if value is not "":
                    dict_fields[keys.pop()] = value
                elif parseEmpty:
                    keys.pop()
                elif emptyValue:
                    dict_fields[keys.pop()] = '"{0}"'.format(emptyValue)
            return dict_fields
        else:
            return fields


class StixFile(object):
    def __init__(self):
        self._rawfile = None
        self._action = 'OtherAction'
        self._elements = None
        self._sources = None
        self._stix_elements = None
        self._rules = {}  # fully parsed rules
        self._full_rules = []  # full context of rules

    def isWhitelisted(self, wl):
        """Return whether or not this Alert is whitelisted"""
        # TODO: currently not supporting white listing
        return False

    def getAction(self):
        return self._action

    def setRawFile(self, file):
        self._rawfile = file

    def getRawFile(self):
        return self._rawfile

    def setStixElements(self, elements):
        self._stix_elements = elements

    def getStixElements(self):
        return self._stix_elements

    def setRules(self, rules):
        self._rules = rules

    def getRules(self, key=None):
        ret = {}

        # TODO: grab the list of rules for the dictionary key
        if key in self._rules:
            return self._rules[key]
        else:
            return self._rules

    def setFullRules(self, rules):
        self._full_rules = rules

    def getFullRules(self):
        return self._full_rules


class RuleFile(object):
    def __init__(self):
        self._rawfile = None
        self._action = 'OtherAction'
        self._sources = None
        self._rules = {}  # fully parsed rules

    def isWhitelisted(self, wl):
        """Return whether or not this Alert is whitelisted"""
        # TODO: currently not supporting white listing
        return False

    def getAction(self):
        return self._action

    def setRawFile(self, file):
        self._rawfile = file

    def getRawFile(self):
        return self._rawfile

    def setRules(self, rules):
        self._rules = rules

    def getRules(self, key=None):
        # grab the list of rules for the dictionary key
        if key in self._rules:
            return self._rules[key]
        else:
            return self._rules

class QueryFields(object):
    """
    Class to aid in properly formatting fields as strings and checking for existence of query fields
    """
    def __init__(self):
        self._fields = {"indicator": "S", "indicatorType": "S", "action": "S",
                        "uuid": "S", "originator": "S", "query_str": "S"}

    def isValid(self, field):
        return field in self._fields

    def getStringRepresentation(self, field, val):
        """Return a string representation of the specified field"""
        #NOTE: Method seems to be redundant. Replaced with a call that just casts the field value to a str.
        # Will remove this function later. 
        if not self.isValid(field):
            raise Exception("Alert field {0} is not a valid field".format(field))
        ftype = self._fields[field]
        if ftype == "I":
            if val is not None:
                return val
            else:
                return ""
        elif ftype == "S":
            if val is not None:
                return val
            else:
                return ""
        elif ftype == "E":
            if val is not None:
                return '"' + val.name + '"'
            else:
                return ""

    @property
    def fields(self):
        return self._fields


class QueryFile(object):
    """The QueryFile object represents the DSearch Query API flow"""
    _queryFields = QueryFields()

    @staticmethod
    def isValidField(field):
        return QueryFile._queryFields.isValid(field)

    def __init__(self):
        self._indicator = None
        self._indicatorType = None
        self._action = None
        self._uuid = None
        self._originator = None
        self._query_str = None

    # setters
    def setFromDict(self, d):
        """Set the fields from the dictionary"""
        if 'indicator' in d:
            self._indicator = d['indicator']
        if 'indicatorType' in d:
            self._indicatorType = d['indicatorType']
        if 'action' in d:
            self._action = d['action']
        if 'uuid' in d:
            self._uuid = d['uuid']
        if 'originator' in d:
            self._originator = d['originator']
        if 'query_str' in d:
            self._query_str = d['query_str']

    def isWhitelisted(self, wl):
        """Return whether or not this Alert is whitelisted"""
        # TODO: currently not supporting white listing
        return False

    def getIndicator(self):
        return self._indicator

    def getIndicatorType(self):
        return self._indicatorType

    def getAction(self):
        return self._action

    def getUUID(self):
        return self._uuid

    def getOriginator(self):
        return self._originator

    def getQueryString(self):
        return self._query_str

    def getFields(self, fieldNames, dictionary=False):
        fields = []
        for field in fieldNames:
            fields.append(str(self._getField(field)))
            # fields.append(QueryFile._queryFields.getStringRepresentation(field, self._getField(field)))

        # uses zip functions to convert the two lists into a dictionary. fieldNames used as keys, fields as values
        if dictionary:
            fields = dict(zip(fieldNames, fields))

        return fields

    def _getField(self, field):
        val = None
        tfld = "_" + field
        if hasattr(self, tfld):
            val = getattr(self, tfld)
        return val

    def getAllFields(self, dictionary=False, parseEmpty=False, emptyValue=None):
        """
        Method to get all supported fields from the intermediate data format.
        :param dictionary: Option to return the results as a dictionary. Defaults to False.
        :param parseEmpty: Option to parse out any empty values.
        :param emptyValue: Option to fill in empty fields with a different value
        :return: Returns either a list or dictionary of all fields and their parsed value. Defaults to a list.
        """
        keys = list(QueryFile._queryFields.fields.keys())
        fields = self.getFields(keys)
        if dictionary:
            dict_fields = {}
            keys.reverse()
            for value in fields:
                if value is not "":
                    dict_fields[keys.pop()] = value
                elif parseEmpty:
                    keys.pop()
                elif emptyValue:
                    dict_fields[keys.pop()] = '"{0}"'.format(emptyValue)
            return dict_fields
        else:
            return fields