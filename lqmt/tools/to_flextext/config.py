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
        self.flext_config = 'resources/sampleConfigurations/flextext.cfg'
        self.config_dict = {}
        self.config_str = ""
        self.source_configs = {
            'Cfm13Alert': 'resources/sampleConfigurations/cfm13.cfg',
            'Cfm20Alert': 'resources/sampleConfigurations/cfm20alert.cfg',
            'stix-tlp': 'resources/sampleConfigurations/stix_tlp.cfg'
        }

        self.fileParser = self.validation('fileParser', str, default="CSV")
        self.fields = self.validation('fields', str, required=True)
        self.delimiter = self.validation('delimiter', str, required=True)
        self.quote_char = self.validation('quoteChar', str, required=True)
        self.escape_char = self.validation('escapeChar', str, required=True)
        self.header_line = self.validation('headerLine', bool, default=True)
        self.double_quote = self.validation('doubleQuote', bool)
        self.quote_style = self.validation('quoteStyle', str, default="none")
        self.primary_schema_config = self.validation('primarySchemaConfig', str,
                                                     default="resources/schemaDefinitions/lqmtools.json")
        self.increment_file = self.validation('incrementFile', bool)
        self.file = self.validation('fileDestination', str, required=True)

        if self.file:
            increment = ""
            filebase, text = os.path.splitext(self.file)
            if self.increment_file:
                increment = "."
                increment += datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

            self.file_destination = filebase + increment + text

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
        self.config_str += "\nDelimiter='" + self.delimiter + "'"
        self.config_str += "\nQuoteChar=" + self.quote_char
        self.config_str += "\nEscapeChar=" + self.escape_char
        self.config_str += "\nHeaderLine=" + str(self.header_line)
        self.config_str += "\nDoubleQuote=" + str(self.double_quote)
        self.config_str += "\nQuoteStyle=" + str(self.quote_style)
        self.config_str += "\n[SCHEMA]"
        self.config_str += "\nPrimarySchemaConfiguration=" + self.primary_schema_config

        return self.config_str
