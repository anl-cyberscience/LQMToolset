import logging
import requests
import time
from xml.etree import ElementTree


def create_message(alert, fields):
    """
    Creates a key-value formatted message for Splunk that contains parsed data from FlexT. Defaulting to parsing
    empty values.

    :param alert: Parsed alert data from FlexT
    :return: Returns formatted string.
    """
    if "all" in fields:
        data = alert.getAllFields(dictionary=True, parseEmpty=True)
    else:
        data = alert.getFields(fields, dictionary=True)

    message = "{0} LQMT: ".format(time.asctime())
    for key, value in data.items():
        if value is "":
            value = None

        message += "{0}={1} ".format(key, value)

    return message


def formatUrlParam(parameter, value, addition=False):
    """
    Function used to format a string of URL parameters. Example output: "user=bob&title=builder"
    :param parameter: URL parameter that the value will be assigned to
    :param value: Value that will be assigned to the provided URL parameter
    :param addition: True or false value to indicate if this parameter is being added as an addition to other values.
    :return: If a valid value is given, a formatted string is returned. Otherwise an empty string is returned.
    """
    if addition:
        addition = "&"
    else:
        addition = ""

    if value:
        return "{}{}={}".format(addition, parameter, value)
    else:
        return ""


class ApiHandler:
    """
    Class for handling API calls to Splunk's REST Api. This class might end up being redundant depending on a few
    things, but that will be fleshed out further as the tool is built.
    """

    def __init__(self, host=None, port=None, username=None, password=None, splunk_token="", cert_check=True,
                 source=None, sourcetype=None, index=None):
        self._messages_processed = 0
        self._logger = logging.getLogger("LQMT.Splunk.ApiCaller")
        self.host = host
        self.port = port
        self.source = formatUrlParam("source", source)
        self.sourcetype = formatUrlParam("sourcetype", sourcetype, True)
        self.index = formatUrlParam("index", index, True)
        self.cert_check = cert_check
        self.url = self.host + ":" + str(self.port)
        self.username = username
        self.password = password
        self.requests = requests
        self.authenticated = False
        self.splunk_token = {'Authorization': splunk_token}
        self.auth_service = "/services/auth/login/"
        self.stream_service = "/services/receivers/stream/"
        self.headers = {}

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
        # Check to make sure we aren't already authenticated
        if not self.authenticated:
            # Format username and password, then send the request
            data = {'username': self.username, 'password': self.password}
            r = self.requests.post(self.url + self.auth_service, data=data, verify=self.cert_check)

            # If authentication is successful, then pull out the token and set our auth status. If not, weep.
            if r.ok:
                data = ElementTree.fromstring(r.content)
                self.splunk_token['Authorization'] = "Splunk " + data[0].text
                self.authenticated = True
                self._logger.debug(
                    "Successfully authenticated with Splunk instance. Token received: {0}".format(data[0].text)
                )
                # Format headers. Currently using splunks streaming input. Could be opened up later to let the user
                # choose.
                self.headers.update(self.splunk_token)
                self.headers.update({"x-splunk-input-mode": "streaming"})
            else:
                r.raise_for_status()

            return self.splunk_token

    def send_message(self, message, source=None, sourcetype=None, index=None):
        """
        Method for sending messages to Splunk via REST api. If the authentication function hasn't been run yet, then
        it is called.
        :param source: Used to override previously set source value
        :param sourcetype: Used to override previously set sourcetype
        :param index:
        :param message: message to be sent to splunk
        """

        # Override's for source, sourcetype, and index
        if source is not None:
            self.source = formatUrlParam("source", source)

        if sourcetype is not None:
            self.sourcetype = formatUrlParam("sourcetype", sourcetype, True)

        if index is not None:
            self.index = formatUrlParam("index", index, True)

        # If not authenticated, then authenticate
        if not self.authenticated:
            self.authenticate()

        # Build url for api and send the api request
        url = self.url + self.stream_service + "?{0}{1}{2}".format(
            self.source,
            self.sourcetype,
            self.index
        )

        r = self.requests.post(url, data=message, headers=self.headers, verify=self.cert_check)

        # If parsed successfully, tally and move on. Otherwise raise status
        if r.ok:
            self._messages_processed += 1
        else:
            r.raise_for_status()

        self._logger.debug("Message sent to Splunk. "
                           "\nURL Used: '{0}'; "
                           "\nStatus code returned: '{1}';".format(url, r.status_code))

    def getTotalMessagesProcessed(self):
        return self._messages_processed
