import importlib
import sys
import logging
import toml

from lqmt.lqm.tool import ToolChain
from lqmt.whitelist.master import MasterWhitelist
from lqmt.lqm.logging import LQMLogging
from lqmt.lqm.sourcedir import DirectorySource
from lqmt.lqm.exceptions import ConfigurationError
from lqmt.lqm.systemconfig import SystemConfig

sys.path.append('tpl/toml')

class ToolInfo():
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


class LQMToolConfig():
    """Holds the Configuration data for the LQMTool"""

    def __init__(self, configfile):
        self._logger = logging.getLogger("LQMT.Config")
        self._sources = []
        self._parsers = {}
        self._toolChains = []
        self._whitelist = None
        self._loggingCfg = None
        self._toolsList = []

        # load config files
        self._loadSystemConfig()
        self._loadUserConfig(configfile)
        # initialize logging
        self._initializeLogging()
        # process config files
        toolClasses = self._processSystemConfig()
        self._processUserConfig(toolClasses)
        if (not self._sources):
            raise ConfigurationError("No sources specified")

    def _loadSystemConfig(self):
        """Load the System configuration file"""
        sysconf = SystemConfig()
        self._config = sysconf.getConfig()

    def _processSystemConfig(self):
        self._initParserConfig(self._config)
        toolClasses = self._initToolConfig(self._config)
        return toolClasses

    def _initParserConfig(self, config):
        parsers = config['parsers']
        if ('additional_paths' in parsers):
            add_path = parsers['additional_paths']
            del parsers['additional_paths']
            sys.path.extend(add_path)
        path = None
        if 'path' in parsers:
            path = parsers['path']
            del parsers['path']
        # path info is loaded from the config files
        for key in list(parsers.keys()):
            parserinfo = parsers[key]
            if (path != None):
                sys.path.append(path)
            importlib.import_module(parserinfo['module'])
            mod = importlib.import_module(parserinfo['module'] + ".parser")
            parserClass = getattr(mod, parserinfo['parser_class'])
            parserConfig = None
            if ("configs" in parserinfo):
                parserConfig = parserinfo['configs']
            parser = None;
            if (parserConfig != None):
                parser = parserClass(parserConfig)
            else:
                parser = parserClass()
            self._parsers[parserinfo['format']] = parser
            self._logger.debug("Loaded parser: %s" % parserinfo['format'])

    def _initToolConfig(self, config):
        """Set up the system path for the configured tools and
        create the configuration data for those tools so they can be created later"""
        tooldefs = config['tools']
        if 'path' in tooldefs:
            path = tooldefs['path']
            # add any paths specified to the system path
            sys.path.append(path)
            del tooldefs['path']
        toolClasses = {}
        for key in list(tooldefs.keys()):
            toolinfo = tooldefs[key]
            if ('additional_paths' in toolinfo):
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
            self._logger.debug("Loaded tool: %s" % key)
        return toolClasses

    def _loadUserConfig(self, configFile):
        cfg = open(configFile)
        topLevelConfig = toml.loads(cfg.read())
        cfg.close()
        self._userConfig = {}
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
        globalTools = self._createTools(self._userConfig, toolClasses)
        self._createToolChains(self._userConfig, globalTools)

        # process any includes
        if 'includes' in self._userConfig:
            for incl in self._userConfig['includes']:
                cfg = open(incl)
                config = toml.loads(cfg.read())
                cfg.close()
                # add any sources specified, if any
                self._addSourcesConfig(config)
                # and create all tools/tool chains specified
                localTools = self._createTools(config, toolClasses)
                self._createToolChains(config, localTools, globalTools)

    def _createTools(self, config, toolClasses):
        if 'Tools' not in config:
            return
        tools = config['Tools']

        theseTools = {}
        for key in tools:
            if key in toolClasses:
                toolInfo = toolClasses[key]
                self._toolsList.append(key)
                for cfgData in tools[key]:
                    tool = toolInfo.create(cfgData, toolClasses['CSV'], self._config['UnprocessedCSV'])
                    tool.toolName = key
                    theseTools[tool.getName()] = tool
        return theseTools

    def _createToolChains(self, config, localTools, globalTools=None):
        if 'ToolChains' not in config:
            return

        chains = config['ToolChains']
        for chainCfg in chains:
            if 'active' in chainCfg and chainCfg['active'] == True:
                self._toolChains.append(self._createToolChain(chainCfg, localTools, globalTools))
            else:
                self._logger.info("Toolchain {0} is currently set as inactive in the user configuration. "
                                  "Tools in this toolchain will not run.".format(chainCfg['name']))

    def _createToolChain(self, chainCfg, localTools, globalTools):
        chain = []
        allEnabled = True
        for toolName in chainCfg['chain']:
            if toolName in localTools:
                tool = localTools[toolName]
            elif globalTools != None and toolName in globalTools:
                tool = globalTools[toolName]
            else:
                raise ConfigurationError("Named tool not found: " + toolName)
            chain.append(tool)
            allEnabled = allEnabled and tool.isEnabled()
            if (not tool.isEnabled()):
                self._logger.error("Tool chain {0} is disabled due to tool {1} being disabled".format(chainCfg['name'],
                                                                                                      tool.getName()))

        chain = ToolChain(chain, chainCfg['name'], enabled=allEnabled)
        if (allEnabled):
            self._logger.info("Created tool chain: {0}".format(chain.getName()))
        chain.printTools()
        return chain

    def _addSourcesConfig(self, config):
        if ('Source' not in config):
            return
        srcCfgs = config["Source"]

        for key in srcCfgs:
            for cfg in srcCfgs[key]:
                if (key == "Directory"):
                    self._sources.append(DirectorySource(cfg))

    def getSources(self):
        return self._sources

    def getParser(self, fmt):
        if (fmt not in self._parsers):
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
