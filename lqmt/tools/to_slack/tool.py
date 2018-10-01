import logging

from slackclient import SlackClient

from lqm.data import AlertAction
from lqm.tool import Tool


class ToSlack(Tool):
    def __init__(self, config):
        """
        ToSlack tool
        :param config: Configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger("LQMT.ToSlack.{0}".format(self.getName()))
        self._sc = None

    def initialize(self):
        super().initialize()
        self._sc = SlackClient(self._config.token)

    def process(self, alert, meta=None):
        try:
            result = self._sc.api_call(
                'files_upload',
                channels=self._config.channels,
                filename=alert.getName(),
                title=self._config.title,
                initial_comment=self._config.body,
                file=alert.getBinFile()
            )
        except Exception as e:
            self._logger.error('Error={}'.format(e))


    def commit(self):
        pass

    def cleanup(self):
        pass