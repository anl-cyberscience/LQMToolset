import os
import logging
import datetime
from lqmt.lqm.tool import ToolConfig
from lqmt.lqm.systemconfig import SystemConfig
from pkg_resources import get_distribution



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

        # FlexTransform configuration variables
        self.header_line = False
        self.increment_file = False
        self.flext_config = 'resources/sampleConfigurations/flextext.cfg'
        self.system_config = SystemConfig()
        self.system_config = self.system_config.getConfig()
        self.config_dict = {}
        self.config_str = ""

        # Configure FlexT parsers based on system configuration
        self.source_configs = {}
        for parser_name, parsers in self.system_config['parsers'].items():
            # Exceptions: LQMTools is a part of every set of parser
            del (parsers['configs']['LQMTools'])

            # If it's more specific, like MBL, then you need to first check that it exists first during iteration by
            # checking the parser_name
            if parser_name == 'mbl':
                del (parsers['configs']['mbl'])

            # Temporary fix for failing tests. Tests fail due to current FlexT version. Once FlexT version 1.2.1 is
            # released, this fix can be removed. 
            ft_version = get_distribution('FlexTransform').version
            ft_version = tuple([int(x) for x in ft_version.split('.')])
            if ft_version < (1, 2, 1):
                if "IID" in parser_name:
                    del (parsers['configs'][parser_name])


            # after the exceptions, update the source_configs with remaining parser configs
            self.source_configs.update(parsers['configs'])

        # FlexText configuration variables
        self.fileParser = self.validation('fileParser', str, default="CSV")
        self.delimiter = self.validation('delimiter', str, required=True)
        self.quote_char = self.validation('quoteChar', str, required=True)
        self.escape_char = self.validation('escapeChar', str, required=True)
        self.header_line = self.validation('headerLine', bool, default=True)
        self.double_quote = self.validation('doubleQuote', bool)
        self.quote_style = self.validation('quoteStyle', str, default="none")
        self.primary_schema_config = self.validation('primarySchemaConfig', str, default="resources/schemaDefinitions"
                                                                                         "/lqmtools.json")
        self.increment_file = self.validation('incrementFile', bool)
        self.file = self.validation('fileDestination', str, required=True)

        # fields variable is configured differently for legacy purposes. The fields variable was originally a string,
        # so we are first checking to see if it's a string (legacy configs), if so we convert it to a list. Then we
        # validate it.
        if 'fields' in config_data:
            if isinstance(config_data['fields'], str):
                config_data['fields'] = config_data['fields'].split(',')

            self.fields = self.validation('fields', list, required=True)

        if self.increment_file:
            base, extension = os.path.splitext(self.file)
            file_name = "." + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            self.file_destination = base + file_name + extension

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
                'Fields': ','.join(self.fields),
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
        self.config_str += "\nFields=" + ','.join(self.fields)
        self.config_str += "\nDelimiter='" + self.delimiter + "'"
        self.config_str += "\nQuoteChar=" + self.quote_char
        self.config_str += "\nEscapeChar=" + self.escape_char
        self.config_str += "\nHeaderLine=" + str(self.header_line)
        self.config_str += "\nDoubleQuote=" + str(self.double_quote)
        self.config_str += "\nQuoteStyle=" + str(self.quote_style)
        self.config_str += "\n[SCHEMA]"
        self.config_str += "\nPrimarySchemaConfiguration=" + self.primary_schema_config

        return self.config_str
