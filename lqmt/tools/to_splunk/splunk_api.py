from xml.etree import ElementTree
import logging
import requests
from lqmt.lqm.exceptions import AuthenticationError


class ApiCaller:
    """
    Class for handling API calls to Splunks REST Api. This class might end up being redundant depending on a few things,
    but that will be fleshed out further as the tool is built.
    """

    def __init__(self, host=None, port=None, username=None, password=None, splunk_token="", cert_check=True):
        self.logger = logging.getLogger("LQMT.Splunk.ApiCaller")
        self.host = host
        self.port = port
        self.cert_check = cert_check
        self.url = self.host + ":" + str(self.port)
        self.username = username
        self.password = password
        self.response = ""
        self.requests = requests
        self.job_status = ""
        self.job_id = ""
        self.authenticated = False
        self.splunk_token = {'Authorization': splunk_token}
        self.auth_service = "/services/auth/login/"
        self.oneshot_service = "/services/"

    def __enter__(self):
        self.authenticate()
        return self

    def __exit__(self, exc_t, exc_v, trace):
        self.requests.post(url=self.url, headers={'Connection': 'close'}, verify=self.cert_check)

    def authenticate(self):
        """
        Method for authenticating against Splunk's REST Api. Returns a session token that will be used for future
        connections
        :return: Session token
        """
        if not self.splunk_token['Authorization']:
            print("Authenticating")
            data = {'username': self.username, 'password': self.password}
            r = self.requests.post(self.url + self.auth_service, data=data, verify=self.cert_check)
            print(r.status_code)
            print(r.ok)
            if r.ok:
                data = ElementTree.fromstring(r.content)
                self.authenticated = True
                self.splunk_token['Authorization'] = "Splunk " + data[0].text
            else:
                # self.logger.error("Authentication failed. Please verify the credentials you provided are correct.")
                raise AuthenticationError("Authentication failed with the following http status code and message - "
                                          "Code: {0} "
                                          "Message: {1}".format(r.status_code, r.reason)
                                          )

            return self.splunk_token

    def send_message(self, message):
        """
        Method for sending messages to Splunk via REST api.
        :param message:
        :return:
        """
        if not self.authenticated:
            self.authenticate()
        r = self.requests.get(self.url + "/services/authorization/roles/",  headers=self.splunk_token, verify=self.cert_check)
        print("{0} {1}".format(r.status_code, r.reason))
        print("Message = {0}".format(message))
