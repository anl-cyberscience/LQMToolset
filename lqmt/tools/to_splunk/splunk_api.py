import logging
import requests
import time
from xml.etree import ElementTree

from lqmt.lqm.exceptions import AuthenticationError


def create_message(alert):
    """
    Creates a key-value formatted message for Splunk that contains parsed data from FlexT. Defaulting to parsing
    empty values.

    :param alert: Parsed alert data from FlexT
    :return: Returns formatted string.
    """
    data = alert.getAllFields(dictionary=True, parseEmpty=True)
    message = "{0} LQMT: ".format(time.asctime())
    for key, value in data.items():
        message += "{0}={1} ".format(key, value)

    return message


class ApiCaller:
    """
    Class for handling API calls to Splunk's REST Api. This class might end up being redundant depending on a few
    things, but that will be fleshed out further as the tool is built.
    """

    def __init__(self, host=None, port=None, username=None, password=None, splunk_token="", cert_check=True,
                 source=None, sourcetype=None):
        self._messages_processed = 0
        self._logger = logging.getLogger("LQMT.Splunk.ApiCaller")
        self.host = host
        self.port = port
        self.source = source
        self.sourcetype = sourcetype
        self.cert_check = cert_check
        self.url = self.host + ":" + str(self.port)
        self.username = username
        self.password = password
        self.requests = requests
        self.authenticated = False
        self.splunk_token = {'Authorization': splunk_token}
        self.auth_service = "/services/auth/login/"
        self.stream_service = "/services/receivers/stream/"

        # Call authentication function when class object is created.
        self.authenticate()

    def __enter__(self):
        self.authenticate()
        return self

    def __exit__(self):
        self._logger.debug("Total messages processed: {0}".format(self._messages_processed))
        self.requests.post(url=self.url, headers={'Connection': 'close'}, verify=self.cert_check)

    def authenticate(self):
        """
        Method for authenticating against Splunk's REST Api. Returns a session token that will be used for future
        connections. If authentication fails, then the lqmt closes out with an error.
        :return: String: splunk_token. Value containing the splunk token provided by Splunk
        """
        if not self.authenticated:
            data = {'username': self.username, 'password': self.password}
            r = self.requests.post(self.url + self.auth_service, data=data, verify=self.cert_check)

            if r.ok:
                data = ElementTree.fromstring(r.content)
                self.splunk_token['Authorization'] = "Splunk " + data[0].text
                self.authenticated = True
                self._logger.debug(
                    "Successfully authenticated with Splunk instance. Token received: {0}".format(data[0].text)
                )
            else:
                raise AuthenticationError("Authentication failed with the following http status code and message - "
                                          "Code: {0} "
                                          "Message: {1}".format(r.status_code, r.reason)
                                          )

            return self.splunk_token

    def send_message(self, message, source=None, sourcetype=None):
        """
        Method for sending messages to Splunk via REST api. If the authentication function hasn't been run yet, then
        it is called.
        :param source: Used to override previously set source value
        :param sourcetype: Used to override previously set sourcetype
        :param message: message to be sent to splunk
        """

        if source is not None:
            self.source = source

        if sourcetype is not None:
            self.sourcetype = sourcetype

        if not self.authenticated:
            self.authenticate()

        headers = {"x-splunk-input-mode": "streaming"}
        headers = dict(list(self.splunk_token.items()) + list(headers.items()))
        url = self.url + self.stream_service + "?source={0}&sourcetype={1}".format(self.source, self.sourcetype)
        r = self.requests.post(url, data=message, headers=headers, verify=self.cert_check)
        if r.ok:
            self._messages_processed += 1
        self._logger.debug("Message sent to Splunk. Status code returned: {0}".format(r.status_code))

    def getTotalMessagesProcessed(self):
        return self._messages_processed
