import logging
import requests
import time
import xmltodict
from xml.etree import ElementTree


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
                 source=None, sourcetype=None, index=None, timeout_duration=0):
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
        self.service = {
            'auth': "/services/auth/login/",
            'stream': "/services/receivers/stream/",
            'search': "/services/search/jobs/"}
        self.headers = {}
        self.job_id = ""
        self.response = ""
        self.query = None
        self.timeout_duration = timeout_duration
        self.dispatch_states = ['QUEUED', 'PARSING', 'RUNNING', 'PAUSED', 'FINALIZING', 'FAILED', 'DONE']

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
            r = self.requests.post(self.url + self.service['auth'], data=data, verify=self.cert_check)

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

    def stream_data(self, message, source=None, sourcetype=None, index=None):
        """
        Method for sending messages to Splunk via REST api using the stream endpoint. If the authentication function hasn't been run yet, then
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
        url = self.url + self.service['stream'] + "?{0}{1}{2}".format(
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

    def submit_search(self, message, source=None, sourcetype=None, index=None):
        """
        Method for submitting a search 
        :param message: 
        :param source:
        :param sourcetype:    
        :param index:
        """
        # Override's for source, sourcetype, and index
        if source is not None:
            self.source = formatUrlParam("source", source)

        if sourcetype is not None:
            self.sourcetype = formatUrlParam("sourcetype", sourcetype, True)

        if index is not None:
            self.index = formatUrlParam("index", index, True)
        
        # Authenticatte
        if not self.authenticated:
            self.authenticate()
        
        # Build url
        url = self.url + self.service['search'] 

        # job_id = self.send_post_request(message, url)
        message = {'search': message}
        # r = self.requests.post(url, data=message, headers=self.headers, verify=self.cert_check)
        job_id = self.send_post_request(message, url)
        # print(r.text)
        print(job_id)
        result = self.fetch_job(job_id)

        return result


    def send_post_request(self, message, url):

        self.response = self.requests.post(url, data=message, headers=self.headers, verify=self.cert_check)

        # If parsed successfully, tally and move on. Otherwise raise status
        if self.response.ok:
            root = ElementTree.fromstring(self.response.text)
            self.job_id = root[0].text
            self._messages_processed += 1

        else:
            self.response.raise_for_status()
            self.job_id = "N/A"

        # self._logger.debug("Message sent to Splunk. "
        #                    "\nURL Used: '{0}'"
        #                    "\nMessage Sent: {1}"
        #                    "\nStatus code returned: '{2}'"
        #                    "\nJob ID: {3}".format(url, message, self.response.status_code, self.job_id))

        return self.job_id

    def fetch_job(self, job_id=None):
        """
        Used to fetch the results from a search job
        :param job_id: the Splunk job ID provided after you submit a search request. Defaults to None because if using
        the api, you most likely already have a job id assigned to self.job_id. Override if needed.
        :return:
        """
        job_status = "PENDING"
        sleep_inc = 1
        if job_id is not None:
            self.job_id = job_id

        if self.response.ok:
            while job_status != "DONE":
                self._logger.debug("Fetching Job - Job still pending.")
                status_response = requests.get(self.url + self.service['search'] + job_id + "/",
                                               auth=(self.username, self.password),
                                               verify=self.cert_check)

                if status_response.status_code == 200 and status_response.ok:
                    parsed_state = self.parse_xml_for_state(status_response.text)
                    if parsed_state in self.dispatch_states:
                        job_status = parsed_state

                if job_status != "DONE":
                    # TODO: Update sleep function
                    time.sleep(sleep_inc)
                    sleep_inc += 2

                elif sleep_inc > self.timeout_duration:
                    pass
                    self._logger.exception("Splunk search job has exceeded your defined timeout duration of {0}".format(
                        self.timeout_duration
                    ))
        else:
            self._logger.error("Error authenticating request.")

        self._logger.debug("Job Finished. Fetching results.")
        payload = {'output_mode': 'csv'}
        job_result = requests.get(self.url + "/services/search/jobs/" + job_id + "/results/",
                                  auth=(self.username, self.password), verify=False, params=payload)

        return job_result

    def getTotalMessagesProcessed(self):
        return self._messages_processed

    def build_url(self, host, port, service, params):
        url = host + ":" + str(port) + self.service[service] + params

        return url

    @staticmethod
    def write_file(response, file):
        if response:
            f = open(file, 'w')
            f.write(response.text)
            f.close()

    @staticmethod
    def format_url_params(params):
        url_params = "?"
        params = list(filter(None, params))
        for param in params:
            url_params += param + "&"

        return url_params[:-1]

    @staticmethod
    def parse_xml_for_state(content):
        value = None
        xml_dict = xmltodict.parse(content)
        for item in xml_dict['entry']['content']['s:dict']['s:key']:
            if '@name' in item:
                if item['@name'] == "dispatchState":
                    value = item['#text']
        return value