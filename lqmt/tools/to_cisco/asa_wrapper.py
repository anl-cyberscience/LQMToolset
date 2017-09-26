import logging
import requests

class AsaHandler:
    """
    Class for handling API calls to Cisco's ASA Rest API interface. 
    """
    def __init__(self, host=None, username=None, password=None, verify_cert=True):
        self._logger = logging.getLogger("LQMT.ToCisco.AsaHandler")
        self.host = host
        self.username = username
        self.password = password
        self.verify_cert = verify_cert
        self.url = "https://{0}/api/".format(self.host)
        self.authentication = ""

    """
    General request structures. 
    Details in ASA docs: https://www.cisco.com/c/en/us/td/docs/security/asa/api/qsg-asa-api.html#pgfId-57779 
    """
    def _get(self, action):
        request = self.url + action
        return requests.get(request, auth=self.authentication, verify=self.verify_cert)
   
    def _put(self, action, data):
        request = self.url + action
        return requests.put(request, data=data, auth=self.authentication, verify=self.verify_cert)

    def _post(self, action, data=None):
        request = self.url + action
        return requests.post(request, data=data, auth=self.authentication, verify=self.verify_cert)

    def _delete(self, action):
        request = self.url + action
        return requests.delete(request, auth=self.authentication, verify=self.verify_cert)

    def _patch(self, action, data):
        request = self.url + action
        return requests.post(request, data=data, auth=self.authentication, verify=self.verify_cert)

