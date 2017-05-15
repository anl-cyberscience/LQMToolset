import logging
from lqmt.lqm.tool import EgressTool
from lqmt.tools.to_splunk.splunk_api import ApiHandler


class FromMBL(EgressTool):
    def __init__(self, config):
        """
        ToToolName description
        :param config: configuration file
        """
        super().__init__(config)
        print('Init function of FromMBL Tool')
        self._logger = logging.getLogger("LQMT.ToolName.{0}".format(self.getName()))
        self.splunk_handler = ApiHandler(
            self._config.host,
            self._config.port,
            self._config.username,
            self._config.password,
            cert_check=self._config.cert_check,
            source=self._config.source,
            index=self._config.index,

        )
        self.job_id = ""
        self.response = ""

    def initialize(self):
        print("Initialize function of FormMBL Tool")
        # super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        # build url and format message payload
        url = self.splunk_handler.build_url(self._config.host, self._config.port, "search", "")
        message = {"search": self._config.splunk_query}

        # send message via post request. Store job_id
        self.job_id = self.splunk_handler.send_post_request(message, url)

        # fetch job results
        self.response = self.splunk_handler.fetch_job(self.job_id)

    def commit(self):
        print("Commit function of FromMBL Tool")
        # self.write_results(self.response)

    def cleanup(self):
        print("Cleanup function of FromMBL Tool")

    def write_results(self):
        pass
