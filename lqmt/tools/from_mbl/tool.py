import logging
import os
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
        self.write_results()

    def commit(self):
        print("Commit function of FromMBL Tool")
        # self.write_results()

    def cleanup(self):
        print("Cleanup function of FromMBL Tool")

    def write_results(self):
        if self._config.output_directory is not None:
            file = self._config.output_directory

            file_dir = os.path.dirname(file)
            if not os.path.exists(file_dir):
                os.makedirs(file_dir, 0o755, True)
            if not os.path.exists(file):
                open(file, 'w').close()

            if self.response is not None:
                results = self.response.text
                with open(file, 'r+') as output_file:
                    output_file.write(results)
