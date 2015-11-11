# Contribute
The Last Quarter Mile Toolset is designed to make creating your own tools easy. 

## Github
LQMT can be found on Github using the following link: <https://github.com/anl-cyberscience/LQMToolset>

After [forking](https://guides.github.com/activities/forking/) the LQMToolset, you can start developing your own tools. Once you are ready, you can contribute by adding your tool to the project through a pull request. 

## Tools
It is expected that most contributions will be adding support of a specific kind of endpoint device, in the majority of cases this will involve the writing of a new tool. Tools, which are found under `LQMToolset/lqmt/tools`, are the modular pieces of LQMT that take the processed CTI data and deliver it to an endpoint device. Since the way endpoint devices receive data differs, tools can vary in design and complexity. For the most part though, all tools follow a basic structure that requires a `config.py` and `tool.py` file. A directory for a tool typically looks like this:

- to_toolname
    - `__init__.py`
    - `config.py`
    - `tool.py`

For clarify sake all tool names follow a convention of "'direction of data flow'_'name of tool'". So in the case of our tool used for pushing data *to syslog*, we name it `to_syslog`. 

### Config.py
*Located under [LQMToolset/lqmt/tools](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/)*

The config.py file is used to define the configurtion of a tool. Here you will define values that will be used and parsed out of the user configuration file. Typically in the config.py file you will define static variables, some functions, and also do some light data parsing. This is also where you should validate values coming in from the user configuration file that relates to your specific tool. 

A good example to look in relation to config.py in the current code base would be the [to_syslog](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/to_syslog/config.py) tool. In a snippit below, you can see default values, such as a defult port, defined under the tools `__init__` definition. Here we can also see the validation values from the userconfig file, specifically we are checking to make use the 'host' is specified in the config. Compare the code snippit below with the user configuration example below it to see how the two influence and integrate with each other. 

Since each tool is unique, not every config will follow this style. We encourage you to do what you feel is right for the tool you are devleoping. 

#### Example of config.py file for the to_syslog tool
```python
class SysLogConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        ToolConfig.__init__(self, configData, csvToolInfo, unhandledCSV)
        self._logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))
        hasError = False
        self._port = 514  # default port for syslog is 514.

        if 'host' in configData:
            self._host = configData['host']
        else:
            self._logger.error("Host must be specified in the configuration")
            hasError = True
```
#### Example of a user configuration for using to_syslog
```toml
[[Tools.SysLog]]
  name = "syslog-tool"
  host = "syslog.it.weylandyutani.com"
  port = 514
  protocol = "tcp"
  messageHead = "wu.server.com LQMTool: Message from LQMT - "
  messageFields = ["indicatorType", "indicator", "action1", "directSource", "reason1", "duration1"]
```

### Tool.py
*Located under [LQMToolset/lqmt/tools/](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/)*

The tool.py compontent of a LQMT tool is, unsurprisingly, where the core functionality of a LQMT tool is developed. This is where most of the heavy lifting of a tool should be integrated. Tool.py is also where the interaction between the core of LQMT and the tool is established, most notably in the generic `process` function, which is directly invoked by the core process of LQMT for all tools. The example shell below gives a picture of the basic structure most tools follow in LQMT. 

It's worth noting again that all tools are unique; not every tool will fit into the same structure as the examples given here. Looking at current tools in the project you will notice many vary in different ways. 

#### Example of tool.py file, derived from to_syslog tool
```python
class ToSysLog(Tool):
    def __init__(self, config):
        Tool.__init__(self, config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))
        self._totalSent = 0
        self._messageHead = config.getMessageHead()
        self._messageFields = config.getMessageFields()
```
#### Example shell of a tool.py file
```python
class toolname(Tool):
    def __init__(self, config):
        Tool.__init__(self, config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))

    def initialize(self):
        super().initialize()

    def process(self, data):
        pass

    def commit(self):
        pass

    def cleanup(self):
        pass
```

### Systemconfig.py
*Located under [LQMToolset/lqmt/lqm/](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/lqm/)*

Systemconfig.py is where main components of LQMT are defined and accessed by LQMT's processing core; all tools that can be used by LQMT are defined here for easy access. After you finish writing your tool you need to define it in the dictionary titled `self.system_config` which is located in the systemconfig.py file. Below is a code template that you can use; just replace all values surrounded by asterisks(*) to match values from your tool. The sample below the template shows that that template looks like with values from the to_syslog tool filled in. 

#### Template:
```python
'*NameofTool*': {
    'module': '*toolname*', 'config_class': '*name of class(defined in config.py)*', 'tool_class': '*name of class(defined in tool.py)*'
},
```
#### Sample from to_syslog:
````python
'SysLog': {
    'module': 'to_syslog', 'config_class': 'SysLogConfig', 'tool_class': 'ToSysLog'
},
````
