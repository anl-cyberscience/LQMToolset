"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
import mattermostdriver

from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToMattermost(Tool):
    def __init__(self, config):
        """
        ToMattermost tool.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger("LQMT.ToMattermost.{0}".format(self.getName()))

        self.client = mattermostdriver.Driver({
            'scheme': self._config.scheme,
            'url': self._config.url,
            'port': self._config.port,
            'login_id': self._config.login,
            'password': self._config.password
        })
        self.client.login()  # TODO - add error handling for incorrect server/username/password/timeout
        self._logger.debug('Mattermost server login')


    def initialize(self):
        super().initialize()

    def process(self, pdf):
        """
        Process function.  Handles the processing of data for the tool.

        :param alerts: Binary PDF file object
        :return None:
        """
        # TODO - add error handling for insufficient permissions to upload file to channel, post in channel
        upload_resp = self.client.files.upload_file(self._config.channel_id,
                                                    files={'files': (pdf.name, pdf.getBinFile())})
        # TODO - add logic for lack of success of file upload in previous statement
        post_resp = self.client.posts.create_post({
            'channel_id': self._config.channel_id,
            'message': 'Upload from LQMT',
            'file_ids': [
                upload_resp['file_infos'][0]['id']
            ]
        })

    def commit(self):
        pass

    def cleanup(self):
        self.client.logout()
        self._logger.debug('Mattermost sever logout')

