import logging
import os
import inspect
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool
from FlexTransform import FlexTransform


class ToFlexText(Tool):
    def __init__(self, config):
        Tool.__init__(self, config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        self._totalSent = 0
        self._transform = FlexTransform.FlexTransform()
        currentdir, name = os.path.split(inspect.getfile(FlexTransform))

        #add cfm13alert parser
        Cfm13AlertConfig = open(
            os.path.join(currentdir, self._config.cfm13Config),
            'r')
        self._transform.AddParser('Cfm13Alert', Cfm13AlertConfig)

        #add csv parser
        FlexTextConfig = open(
            os.path.join(currentdir, self._config.flexTConfig),
            'r')
        self._transform.AddParser('CSV', FlexTextConfig)

    def initialize(self):
        super().initialize()

    def process(self, datafile):
        """
        Handles the processing of data for the tool.

        The FlexT parser had to be called here despite being called already in the program. Parser is original called
        and used in the controller.py file. The problem is the parser is defined and called based on the type of alerts
        being handled. FlexText doesn't have a specific filetype so the easiest, though not most efficient, path is to
        call a completely separate parser here to handle FlexText parsing on the alerts.

        Args:
            datafile: String that contains the path to the alert being processed.
        """

        self._transform.TransformFile(
            sourceFileName=datafile,
            targetFileName=self._config.fileDestination,
            sourceParserName='Cfm13Alert',
            targetParserName='CSV'
        )

    def commit(self):
        pass

    def cleanup(self):
        pass
