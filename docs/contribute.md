# Contribute
The Last Quarter Mile Toolset is designed in a way so that developing and contributing your own tool extensions is easy. 

## Github
LQMT can be found on Github <https://github.com/anl-cyberscience/LQMToolset>

After [forking](https://guides.github.com/activities/forking/) the LQMT project on Github, you can start to develop your own tools. 

## Tools
It is expected that most contributions will be for support of a specific kind of device, in the majority of cases this will involve the writing of a new tool. Tools, which are found under `LQMToolset/lqmt/tools`, are the modular pieces of LQMT that take the processed CTI data and deliver it to an endpoint device. Since the way endpoint device receive data differs, tools can vary in design and complexity. For the most part though, all tools follow a basic structure that requires a `config.py` and `tool.py` file. A directory for a tool typically looks like this:

- to_toolname
    - `__init__.py`
    - `config.py`
    - `tool.py`

For clarify sake all tool names follow a convention of "'direction of data flow'_'name of tool'". So in the case of our tool used for pushing data *to* *syslog*, we name it `to_syslog`. 

### Config.py
*Located under [LQMToolset/lqmt/tools](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/)*

The config.py file is generally used to manage the configuration of the given tool. It's here you will manage the parsing of the user configuration file for information needed to accomplish the job of your tool. This is also where you would define default values, such as server ports, and define functions for your tool. You should just keep in might any data that you will need to interact with an endpoint device should be defined here so that is can later be accessed in the `tool.py` file. 

A good example in the current code base would be the [to_syslog](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/to_syslog/config.py) tool. In a snippit below, you can see default values, such as a defult port, defined under the tools `__init__` definition. Here we can also see the validation of the userconfig, specifically we are checking to make use the 'host' is specified in the config. 

Since all tools are unique, you can use the config.py file to do other things that might not be covered here. 

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
#### Code snipit used in /lqmt/tools/to_syslog/config.py
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

### Tool.py
*Located under [LQMToolset/lqmt/tools/](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/)*

```python
class ToSysLog(Tool):
    def __init__(self, config):
        Tool.__init__(self, config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))
        self._totalSent = 0
        self._messageHead = config.getMessageHead()
        self._messageFields = config.getMessageFields()
```

The tool.py file is where you will 

### Systemconfig.py
*Located under [LQMToolset/lqmt/lqm/](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/lqm/)*

Systemconfig.py is used for defining and accessing various elements in LQMT. After you finish writing your tool, you need to define it in the system_config dictionary under the "tools" key found in Systemconfig.py. Below is a code template you can use, where you replace all values surrounded by asterisks(*) with values from your tool. There is a code sample below the template to give an example of what this section looks like for the `to_syslog` tool.

#### Template:
```python
'SysLog': {
    'module': '*toolname*', 'config_class': '*name of class(defined in config.py)*', 'tool_class': '*name of class defined in tool.py*'
},
```
#### Sample from to_syslog:
````python
'SysLog': {
    'module': 'to_syslog', 'config_class': 'SysLogConfig', 'tool_class': 'ToSysLog'
},
````