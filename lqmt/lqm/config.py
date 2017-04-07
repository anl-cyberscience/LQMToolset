import importlib
import io
import logging
import os
import sys

import toml

from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.logging import LQMLogging
from lqmt.lqm.sourcedir import DirectorySource
from lqmt.lqm.systemconfig import SystemConfig
from lqmt.lqm.tool import ToolChain
from lqmt.whitelist.master import MasterWhitelist
from lqmt.lqm.parsers.FlexTransform import parser as ft_parser

sys.path.append('tpl/toml')


class ToolInfo:
    """Holds info for future instantiation and instantiates tool instances
    """

    def __init__(self, toolClass, configClass):
        """Hold tool class object and config class object"""
        self._toolClass = toolClass
        self._configClass = configClass

    def create(self, configData, csvToolInfo, unhandledCSV):
        """Create a new config instance from the parameters passed in
        and then create a new tool instace using that configuration"""
        config = self._configClass(configData, csvToolInfo, unhandledCSV)
        tool = self._toolClass(config)
        return tool


class LQMToolConfig(object):
    """Holds the Configuration data for the LQMTool"""

    def __init__(self, configfile):
        self._logger = logging.getLogger("LQMT.Config")
        self._sources = []
        self._parsers = {}
        self._toolChains = {'ingress': [], 'egress': []}
        # self._toolChains = []
        self._whitelist = None
        self._loggingCfg = None
        self._toolsList = []
        self._userConfig = {}

        # load config files
        self._loadSystemConfig()
        self._loadUserConfig(configfile)
        # initialize logging
        self._initializeLogging()
        # process config files
        toolClasses = self._processSystemConfig()
        self._processUserConfig(toolClasses)
        if not self._sources:
            raise ConfigurationError("No sources specified")

    def _loadSystemConfig(self):
        """Load the System configuration file"""
        sysconf = SystemConfig()
        self._config = sysconf.getConfig()

    def _processSystemConfig(self):
        """
        Parses and initializes the system configuration
        :return: toolClasses, which is a dictionary holding classes for the tools assigned in the user configuration
        """
        self._initParserConfig(self._config['parsers'])
        toolClasses = self._initToolConfig(self._config)
        return toolClasses

    def _initParserConfig(self, parsers):
        """
        Initializes parsers using configuration details provided by the system configuration file
        :param parsers: Parser information passed from the system configuration file
        """

        # path info is loaded from the config files
        for key, parserinfo in parsers.items():

            # gets parser class from flexT
            parserClass = getattr(ft_parser, parserinfo['parser_class'])

            # if particular configs were defined for the parser, pass them to FlexT parser and append to self._parsers
            if parserinfo['configs']:
                self._parsers[parserinfo['format']] = parserClass(parserinfo['configs'])
            else:
                self._parsers[parserinfo['format']] = parserClass()

        self._logger.debug("Parsers loaded: %s" % ', '.join(self._parsers.keys()))

    def _initToolConfig(self, config):
        """
        Set up the system path for the configured tools and create the configuration data for those tools so they can
        be created later.
        """

        # Use user configuration to only load tools the user specifies. The CSV tool is appended at the end because
        # it is needed later regardless of what tools are loaded.
        tooldefs = config['tools']
        usertooldefs = []

        for key, config in self._userConfig['Tools'].items():
            usertooldefs.append(key)

        # usertooldefs = self._userConfig['Tools'].keys()
        # usertooldefs = list(usertooldefs)
        usertooldefs.append('CSV')

        # uses dictionary comprehension to filter out only user specified tools from the tooldefs dictionary
        tooldefs = {tool_key: tooldefs[tool_key] for tool_key in usertooldefs}

        toolClasses = {}
        for key in list(tooldefs.keys()):
            toolinfo = tooldefs[key]
            if 'additional_paths' in toolinfo:
                # add any additional paths needed by the tool
                add_path = toolinfo['additional_paths']
                sys.path.extend(add_path)
            # import the tool & config modules
            mod = importlib.import_module("lqmt.tools." + toolinfo['module'] + ".tool")
            toolClass = getattr(mod, toolinfo['tool_class'])
            mod = importlib.import_module("lqmt.tools." + toolinfo['module'] + ".config")
            # get the class "object" for later creation
            cfgClass = getattr(mod, toolinfo['config_class'])
            toolClasses[key] = ToolInfo(toolClass, cfgClass)

        self._logger.debug("Loading the following tools: %s" % ', '.join(tooldefs))
        return toolClasses

    def _loadUserConfig(self, configFile):
        """
        Loads the user configuration file
        :param configFile: String that defines the path of the user configuration file.
        """
        # if provided config is an existing directory, open and read the file. Else it is assumed to be a config string
        if os.path.exists(configFile):
            cfg = open(configFile)
            topLevelConfig = toml.loads(cfg.read())
            cfg.close()
        else:
            configFile = io.StringIO(configFile)
            topLevelConfig = toml.load(configFile)

        self._userConfig.update(topLevelConfig)

    def _initializeLogging(self):
        if 'Logging' in self._userConfig:
            self._loggingCfg = LQMLogging(self._userConfig['Logging'])

    def _processUserConfig(self, toolClasses):
        """Process the user-level configuration"""

        # Add any sources specified
        self._addSourcesConfig(self._userConfig)

        # If a whitelist was specified, create it
        if 'Whitelist' in self._userConfig:
            self._whitelist = MasterWhitelist(configData=self._userConfig['Whitelist'])

        # create any tools and tool chains in the top-level user config file
        tools = self._createTools(self._userConfig, toolClasses)
        self._createToolChains(self._userConfig, tools)

    def _createTools(self, config, toolClasses):
        if 'Tools' not in config:
            return
        tools = config['Tools']

        theseTools = {'ingress': {}, 'egress': {}}
        for key in tools:
            if key in toolClasses:
                toolInfo = toolClasses[key]
                self._toolsList.append(key)
                for cfgData in tools[key]:
                    tool = toolInfo.create(cfgData, toolClasses['CSV'], self._config['UnprocessedCSV'])
                    tool.toolName = key
                    theseTools[self.get_tool_type(key)][tool.getName()] = tool
        return theseTools

    @staticmethod
    def get_tool_type(toolname):
        tool_type = 'egress'
        if 'from' in toolname.lower():
            tool_type = 'ingress'

        return tool_type

    def _createToolChains(self, config, localTools, globalTools=None):
        if 'ToolChains' not in config:
            return

        chains = config['ToolChains']
        for chainCfg in chains:
            if 'active' in chainCfg and chainCfg['active'] is True:
                self._createToolChain(chainCfg, localTools, globalTools)
                # self._toolChains.append(self._createToolChain(chainCfg, localTools, globalTools))
            else:
                self._logger.info("Toolchain {0} is currently set as inactive in the user configuration. "
                                  "Tools in this toolchain will not run.".format(chainCfg['name']))

    def _createToolChain(self, chainCfg, localTools, globalTools):
        chain = {'ingress': [], 'egress': []}
        # chain = []
        allEnabled = True
        for tool_type, tools in localTools.items():
            for toolName in chainCfg['chain']:
                if toolName in tools:
                    tool = tools[toolName]
                elif globalTools is not None and toolName in globalTools:
                    tool = globalTools[toolName]
                else:
                    # TODO: Reestablish process for raising configuration error when tool is not found
                    break
                    # raise ConfigurationError("Named tool not found: " + toolName)
                chain[tool_type].append(tool)
                allEnabled = allEnabled and tool.isEnabled()
                if not tool.isEnabled():
                    self._logger.error("Tool chain {0} is disabled due to tool {1} being disabled".format(chainCfg['name'],
                                                                                                      tool.getName()))

        chain = ToolChain(chain, chainCfg['name'], enabled=allEnabled)
        if allEnabled:
            self._logger.info("Created tool chain: {0}".format(chain.getName()))
        chain.printTools()
        # TODO: Need to split egress and ingress tools into their own toolchains. Should setup framework to allow users
        # to configure this, but have a filtering process to catch if they fail to do so.
        self._toolChains.append(chain)

    def _addSourcesConfig(self, config):
        if 'Source' not in config:
            return
        srcCfgs = config["Source"]

        for key in srcCfgs:
            for cfg in srcCfgs[key]:
                if key == "Directory":
                    self._sources.append(DirectorySource(cfg))

    def getSources(self):
        return self._sources

    def getParser(self, fmt):
        if fmt not in self._parsers:
            return None
        return self._parsers[fmt]

    def getToolChains(self):
        return self._toolChains

    def getWhitelist(self):
        return self._whitelist

    def getToolsList(self):
        """
        :return: Returns a list of tools that are currently active in the toolchain.
        """
        return self._toolsList
