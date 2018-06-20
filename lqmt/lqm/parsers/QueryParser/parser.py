"""
Created on Dec 19, 2017

@author: grjohnson
"""
import os
import logging
import json
from lqmt.lqm.data import QueryFile


class QueryParser(object):
    def __init__(self, config=None):
        # currently no config parameters
        self._logger = logging.getLogger("LQMT.Parsers")

    def __extract_query_params(self, data):
        """
        Function that extracts from a DS Query JSON format to a tool format.
        :param data: JSON object that matches the DS Query format
        :return res: Returned parsed query data as a JSON.
        """
        res = {}

        # DS Query has the search at {'query': {'match': {'type':'value'}}}
        if 'query' in data:
            if 'match' in data['query']:
                # TODO: for now iterates and takes last entry
                # TODO: future use case is chained query language
                for key, value in data['query']['match'].items():
                    res['indicatorType'] = key
                    res['indicator'] = value
                # Query must be present in AlertActions class enum
                res['action'] = 'Query'
                # Build a query string, long term would support compound searching
                res['query_str'] = res['indicatorType'] + "=" + res['indicator']
        if 'originator' in data:  # originator of the dsearch query
            res['originator'] = data['originator']
        if 'id' in data:  # this is the dsearch UUID for responses to use
            res['uuid'] = data['id']

        return res

    def custom_parser(self, datafile):
        """
        Function that extracts the DS Query JSON object from the local file.
        :param datafile: Filename to be opened for parsing.
        :return output: Returned parsed query data as a JSON.
        """
        output = {}

        try:
            if os.path.exists(datafile):
                # open the file into a json object
                with open(datafile, 'r') as file:
                    data = json.load(file)
                # parse out the values into a dictionary
                output = self.__extract_query_params(data)
        except Exception as e:
            self._logger.error(
                "LQMT-Query-Parser: Error parsing file. file='{0}' exception='{1}'".format(datafile, e))

        return output

    def parse(self, datafile, meta=None):
        """
        Parse the datafile using the metadata dictionary.

        :param datafile: Contains path to the file containing the alert data.
        :param meta: Contains meta data about the datafile. Examples includes PayloadFormat, FileName, PayloadType, and
        more.
        :return alerts: Returns parsed alert data.
        """
        alerts = []

        # Open the file and parse the DS Query
        try:
            data = self.custom_parser(datafile)
        except Exception as e:
            data = None
            self._logger.error(
                "LQMT-Query-Parser: Error parsing file file='{0}' exception='{1}'".format(datafile, e))

        # Create the object file to pass to the tool chains
        try:
            if data:
                alert = QueryFile()
                alert.setFromDict(data)
                alerts.append(alert)
        except Exception as e:
            self._logger.error("LQMT-Query-Parser: Problem with parsed data. Exception={0}".format(e))

        return alerts
