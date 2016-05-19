import os
import logging
import datetime
from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.tool import ToolConfig


class FlexTextConfig(ToolConfig):
    """
    Configuration Class for FlexText
    """

    def __init__(self, config_data, csvToolInfo, unhandledCSV):
        """
        Constructor
        """
        super().__init__(config_data, csvToolInfo, unhandledCSV)

        self.logger = logging.getLogger("LQMT.FlexText.{0}".format(self.getName()))
        hasError = False

        self.header_line = False
        self.increment_file = False
        self.cfm13_config = 'resources\\sampleConfigurations\\cfm13.cfg'
        self.flext_config = 'resources\\sampleConfigurations\\flextext.cfg'
        self.config_dict = {}
        self.config_str = ""

        if 'fileParser' in config_data:
            self.fileParser = config_data['fileParser']
        else:
            self.logger.error("The parameter 'fileParser' must be specified in the configuration")
            hasError = True

        if 'fields' in config_data:
            self.fields = config_data['fields']
        else:
            self.logger.error("The parameter 'fields' must be specified in the configuration")
            hasError = True

        if 'delimiter' in config_data:
            self.delimiter = config_data['delimiter']
        else:
            self.logger.error("The parameter 'delimiter' must be specified in the configuration")
            hasError = True

        if 'quoteChar' in config_data:
            self.quote_char = config_data['quoteChar']
        else:
            self.logger.error("The parameter 'quoteChar' must be specified in the configuration")

        if 'escapeChar' in config_data:
            self.escape_char = config_data['escapeChar']
        else:
            self.logger.error("The parameter 'escapeChar' must be specified in the configuration")
            hasError = True

        if 'headerLine' in config_data:
            self.header_line = config_data['headerLine']

        if 'doubleQuote' in config_data:
            self.double_quote = config_data['doubleQuote']

        if 'quoteStyle' in config_data:
            self.quote_style = config_data['quoteStyle']
        else:
            self.logger.error("The parameter 'quoteStyle' must be specified in the configuration")
            hasError = True

        if 'primarySchemaConfig' in config_data:
            self.primary_schema_config = config_data['primarySchemaConfig']
        else:
            self.logger.error("The parameter 'primarySchemaConfig' must be specified in the configuration")
            hasError = True

        if 'incrementFile' in config_data:
            self.increment_file = config_data['incrementFile']

        if 'fileDestination' in config_data:
            increment = ""
            file = config_data['fileDestination']
            filebase, text = os.path.splitext(file)
            if self.increment_file:
                increment = "."
                increment += datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            self.file_destination = filebase + increment + text
        else:
            hasError = True
            self.logger.error("'file' must be specified for FlexText tool")

        if hasError:
            self.disable()
            raise ConfigurationError("Missing a required value in the user configuration for the to_flextext tool")

    def config_to_dict(self):
        """
        Takes config vars and turns them into a FlexT compatible config dict; assigns values to config_dict
        :return: returns config_dict var
        """
        self.config_dict = {
            'SYNTAX': {
                'FileParser': self.fileParser
            },
            'CSV': {
                'Fields': self.fields,
                'Delimiter': self.delimiter,
                'QuoteChar': self.quote_char,
                'EscapeChar': self.escape_char,
                'HeaderLine': self.header_line,
                'DoubleQuote': self.double_quote,
                'QuoteStyle': self.quote_style
            },
            'SCHEMA': {
                'PrimarySchemaConfiguration': self.primary_schema_config
            }
        }

        return self.config_dict

    def config_to_str(self):
        """
        Takes config vars and turns them into a FlexT compatible config string; assigns values to config_str
        :return: returns config_str var
        """
        self.config_str += "[SYNTAX]"
        self.config_str += "\nFileParser=" + self.fileParser
        self.config_str += "\n[CSV]"
        self.config_str += "\nFields=" + self.fields
        self.config_str += "\nDelimiter='" + self.delimiter+"'"
        self.config_str += "\nQuoteChar=" + self.quote_char
        self.config_str += "\nEscapeChar=" + self.escape_char
        self.config_str += "\nHeaderLine=" + str(self.header_line)
        self.config_str += "\nDoubleQuote=" + str(self.double_quote)
        self.config_str += "\nQuoteStyle=" + str(self.quote_style)
        self.config_str += "\n[SCHEMA]"
        self.config_str += "\nPrimarySchemaConfiguration=" + self.primary_schema_config

        return self.config_str
