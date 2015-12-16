import os
import logging
import datetime
from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.tool import ToolConfig


class FlexTextConfig(ToolConfig):
    """
    Configuration Class for FlexText
    """

    def __init__(self, configData, csvToolInfo, unhandledCSV):
        """
        Constructor
        """
        super().__init__(configData, csvToolInfo, unhandledCSV)

        self.logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        hasError = False

        self.headerLine = False
        self.incrementFile = False
        self.cfm13Config = 'resources\\sampleConfigurations\\cfm13.cfg'
        self.flexTConfig = 'resources\\sampleConfigurations\\toblock_csv.cfg'

        if 'fileParser' in configData:
            self.fileParser = configData['fileParser']
        else:
            self.logger.error("The parameter 'fileParser' must be specified in the configuration")
            hasError = True

        if 'fields' in configData:
            self.fields = configData['fields']
        else:
            self.logger.error("The parameter 'fields' must be specified in the configuration")
            hasError = True

        if 'delimiter' in configData:
            self.delimiter = configData['delimiter']
        else:
            self.logger.error("The parameter 'delimiter' must be specified in the configuration")
            hasError = True

        if 'quoteChar' in configData:
            self.quoteChar = configData['quoteChar']
        else:
            self.logger.error("The parameter 'quoteChar' must be specified in the configuration")

        if 'escapeChar' in configData:
            self.escapeChar = configData['escapeChar']
        else:
            self.logger.error("The parameter 'escapeChar' must be specified in the configuration")
            hasError = True

        if 'headerLine' in configData:
            self.headerLine = configData['headerLine']

        if 'doubleQuote' in configData:
            self.doubleQuote = configData['doubleQuote']

        if 'quoteStyle' in configData:
            self.quoteStyle = configData['quoteStyle']
        else:
            self.logger.error("The parameter 'quoteStyle' must be specified in the configuration")
            hasError = True

        if 'primarySchemaConfig' in configData:
            self.primarySchemaConfig = configData['primarySchemaConfig']
        else:
            self.logger.error("The parameter 'primarySchemaConfig' must be specified in the configuration")
            hasError = True

        if 'siteSchemaConfig' in configData:
            self.siteSchemaConfig = configData['siteSchemaConfig']
        else:
            self.logger.error("The parameter 'siteSchemaConfig' must be specified in configuration")
            hasError = True

        if 'incrementFile' in configData:
            self.incrementFile = configData['incrementFile']

        if 'fileDestination' in configData:
            increment = ""
            file = configData['fileDestination']
            filebase, fext = os.path.splitext(file)
            if self.incrementFile:
                increment = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            self.fileDestination = filebase + "." + increment + fext
        else:
            hasError = True
            self.logger.error("'file' must be specified for FlexText tool")

        if hasError:
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_flextext tool")
