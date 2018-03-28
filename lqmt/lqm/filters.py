import arrow
from lqmt.lqm.exceptions import ConfigurationError

class SourceFilters(object):
    def __init__(self, config):
        """
        Initialization function for class handling file source filters
        :param config: Dictionary of the user configuration section for Sources.Filters
        :return: None
        """
        self._site_includes = []
        self._site_excludes = []
        self._payload_types = []
        self._payload_formats = []
        self._sensitivities = []
        self._restrictions = []
        self._reconnaissance = []
        self._max_file_age = None

        if 'site_includes' in config:
            self._site_includes = self.__list_lower(config['site_includes'])
        if 'site_excludes' in config:
            self._site_excludes = self.__list_lower(config['site_excludes'])
        if 'payload_types' in config:
            self._payload_types = self.__list_lower(config['payload_types'])
        if 'payload_formats' in config:
            self._payload_formats = self.__list_lower(config['payload_formats'])
        if 'sensitivities' in config:
            self._sensitivities = self.__list_lower(config['sensitivities'])
        if 'restrictions' in config:
            self._restrictions = self.__list_lower(config['restrictions'])
        if 'reconnaissance' in config:
            self._reconnaissance = self.__list_lower(config['reconnaissance'])
        if 'max_file_age' in config:
            self._max_file_age = config['max_file_age']

    def __list_lower(self, value):
        """
        Lower cases a list that is provided.
        :param value: List of strings to be converted to lower case
        :return ret: Converted list
        """
        ret = []

        for i in value:
            ret.append(i.lower())

        return ret

    def checkAllFilters(self, metafile):
        """
        Performs all the available filter checks against the file meta-data.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        if not self.checkSendingSite(metafile):
            return False
        if not self.checkPayloadType(metafile):
            return False
        if not self.checkPayloadFormat(metafile):
            return False
        if not self.checkDataSensitivity(metafile):
            return False
        if not self.checkSharingRestrictions(metafile):
            return False
        if not self.checkReconPolicy(metafile):
            return False
        if not self.checkFileAge(metafile):
            return False

        return True

    def checkSendingSite(self, metafile):
        """
        Checks the Includes and Excludes list against the sending site in the meta data.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        # Check the Sending Sites
        if 'SendingSite' in metafile:
            if metafile['SendingSite'].lower() in self._site_includes or not self._site_includes:
                ret = True
            # if in both includes and excludes, will filter out the file
            if metafile['SendingSite'].lower() in self._site_excludes and self._site_excludes:
                ret = False

        return ret

    def checkPayloadType(self, metafile):
        """
        Checks the Payload Type against configured list.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        if not self._payload_types:
            return True

        # Check the PayloadType
        if 'PayloadType' in metafile:
            if metafile['PayloadType'].lower() in self._payload_types:
                ret = True

        return ret

    def checkPayloadFormat(self, metafile):
        """
        Checks the Payload Format against configured list.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        if not self._payload_formats:
            return True

        # Check the PayloadFormat
        if 'PayloadFormat' in metafile:
            if metafile['PayloadFormat'].lower() in self._payload_formats:
                ret = True

        return ret

    def checkDataSensitivity(self, metafile):
        """
        Checks the Data Sensitivity against configured list.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        if not self._sensitivities:
            return True

        # Check the DataSensitivity
        if 'DataSensitivity' in metafile:
            if metafile['DataSensitivity'].lower() in self._sensitivities:
                ret = True

        return ret

    def checkSharingRestrictions(self, metafile):
        """
        Checks the Sharing Restrictions against configured list.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        if not self._restrictions:
            return True

        # Check the SharingRestrictions
        if 'SharingRestrictions' in metafile:
            if metafile['SharingRestrictions'].lower() in self._restrictions:
                ret = True

        return ret

    def checkReconPolicy(self, metafile):
        """
        Checks the Reconnaissance Policy against configured list.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False

        if metafile is None:
            return False

        if not self._reconnaissance:
            return True

        # Check the ReconPolicy
        if 'ReconPolicy' in metafile:
            if metafile['ReconPolicy'].lower() in self._reconnaissance:
                ret = True

        return ret

    def checkFileAge(self, metafile):
        """
        Checks the Sent Timestamp against a shifted date/time for maximum file age.
        :param metafile: Meta-data file to compare to the filter parameters
        :return: Boolean for whether file has passed the pre-filtering settings
        """
        ret = False
        now = arrow.utcnow()
        filetime = None
        num = 0
        second = ['s', 'sec', 'secs', 'second', 'seconds']
        minute = ['m', 'min', 'minute', 'minutes']
        hour = ['h', 'hr', 'hrs', 'hour', 'hours']
        day = ['d', 'day', 'days']
        week = ['w', 'week', 'weeks']
        month = ['mon', 'month', 'months']
        year = ['y', 'yr', 'yrs', 'year', 'years']

        if metafile is None:
            return False

        if self._max_file_age is None:
            return True

        cols = self._max_file_age.split(' ')
        if cols[0].isdigit():
            num = -1 * int(cols[0])
        else:
            raise ConfigurationError(
                "Unable to parse file age \"{0}\" expecting %d %s format (e.g. 2 weeks)".format(self._max_file_age))

        if cols[1] in second:
            shift = now.shift(seconds=num)
        elif cols[1] in minute:
            shift = now.shift(minutes=num)
        elif cols[1] in hour:
            shift = now.shift(hours=num)
        elif cols[1] in day:
            shift = now.shift(days=num)
        elif cols[1] in week:
            shift = now.shift(weeks=num)
        elif cols[1] in month:
            shift = now.shift(months=num)
        elif cols[1] in year:
            shift = now.shift(years=num)
        else:
            raise ConfigurationError(
                "Unable to determine time string in \"{0}\". Refer to documentation for accepted time strings.".format(self._max_file_age))

        if 'SentTimestamp' in metafile:
            filetime = arrow.get(metafile['SentTimestamp'])
            if filetime > shift:
                ret = True

        return ret

class PostFilter(object):
    def __init__(self, config):
        self.config = config
        self.stuff = None

    def checkAllFilters(self, alert):
        """
        Pass through filter for post-processed data. 
        :param alert: Alert object
        :return Bool
        """

        if not self.checkType(alert._indicatorType, 'indicator_types'):
            return False
        if not self.checkType(alert._directSource, 'direct_sources'):
            return False
        if not self.checkType(alert._action1, 'actions'):
            return False
        if not self.checkType(alert._restriction, 'restrictions'):
            return False
        if not self.checkType(alert._sensitivity, 'sensitivities'):
            return False
        
        return True

    def checkType(self, check, type):
        """
        Function for checking alert type values against filters. 
        :param check: The value being checked
        :param type: The type of filter to check for
        """
        
        # Includes
        if isinstance(check, str): 
            if check.lower() in self.config['include'][type]:
                return True

        # Excludes
        if isinstance(check, str): 
            if check.lower() in self.config['exclude'][type]:
                return False
        
        return True
