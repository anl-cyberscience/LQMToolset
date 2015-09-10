import logging
from lqm.exceptions import ConfigurationError
from lqm.tool import ToolConfig


class FlexTextConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        ToolConfig.__init__(self, configData, csvToolInfo, unhandledCSV)
        self._logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        hasError = False
        self._headerLine = False
        self._headerLine = False

        if 'fileParser' in configData:
            self._fileParser = configData['fileParser']
        else:
            self.logger.error("The parameter 'fileParser' must be specified in the configuration")
            hasError = True

        if 'fields' in configData:
            self._fields = configData['fields']
        else:
            self.logger.error("The parameter 'fields' must be specified in the configuration")
            hasError = True

        if 'delimiter' in configData:
            self._delimiter = configData['delimiter']
        else:
            self.logger.error("The parameter 'delimiter' must be specified in the configuration")
            hasError = True

        if 'quoteChar' in configData:
            self._quoteChar = configData['quoteChar']
        else:
            self.logger.error("The parameter 'quoteChar' must be specified in the configuration")

        if 'escapeChar' in configData:
            self._escapeChar = configData['escapeChar']
        else:
            self.logger.error("The parameter 'escapeChar' must be specified in the configuration")
            hasError = True

        if 'headerLine' in configData:
            self._headerLine = configData['headerLine']

        if 'doubleQuote' in configData:
            self._doubleQuote = configData['doubleQuote']

        if 'quoteStyle' in configData:
            self._quoteStyle = configData['quoteStyle']
        else:
            self.logger.error("The parameter 'quoteStyle' must be specified in the configuration")
            hasError = True

        if 'primarySchemaConfig' in configData:
            self._primarySchemaConfig = configData['primarySchemaConfig']
        else:
            self.logger.error("The parameter 'primarySchemaConfig' must be specified in the configuration")
            hasError = True

        if 'siteSchemaConfig' in configData:
            self._siteSchemaConfig = configData['siteSchemaConfig']
        else:
            self.logger.error("The parameter 'siteSchemaConfig' must be specified in configuration")
            hasError = True

        if hasError:
            self.disable()
            raise ConfigurationError()

    def getFileParser(self):
        return self._fileParser

    def getFields(self):
        return self._fields

    def getDelimiter(self):
        return self._delimiter

    def getQuoteChar(self):
        return self._quoteChar

    def getEscapeChar(self):
        return self._escapeChar

    def getHeaderLine(self):
        return self._headerLine

    def getDoubleQuote(self):
        return self._doubleQuote

    def getQuoteStyle(self):
        return self._quoteStyle

    def getprimarySchemaConfig(self):
        return self._primarySchemeConfig

    def getSiteSchemaConfig(self):
        return self._siteSchemaConfig