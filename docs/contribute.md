# Contribute
The Last Quarter Mile Toolset uses a modular design that makes developing your own tools relatively easy. 

## Github
LQMT can be found on Github using the following link: <https://github.com/anl-cyberscience/LQMToolset>

After [forking](https://guides.github.com/activities/forking/) the LQMToolset, you can start developing your own tools. Once you are ready, you can contribute by adding your tool to the project through a pull request. 

## Tools
It is expected that most contributions will be adding support of a specific kind of endpoint device, in the majority of cases this will involve the writing of a new tool. Tools, which are found under `LQMToolset/lqmt/tools`, are the modular pieces of LQMT that take the processed CTI data and deliver it to an endpoint device. Since the way endpoint devices receive data differs, tools can vary in design and complexity. For the most part though, all tools follow a basic structure that requires a `config.py` and `tool.py` module file. A directory for a tool typically looks like this:

- `to_toolname`
    - `__init__.py`
    - `config.py`
    - `tool.py`

For clarity sake, all tool names follow a convention of "'direction-of-data-flow_name-of-tool'". So in the case of our tool used for pushing data *to syslog*, we name it `to_syslog`. We find this convention intuitive, but the developer of the tool can decide what is appropriate for what they are developing. 

### Config.py
*Located under [LQMToolset/lqmt/tools](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/)*

The `config.py` module is used to define the configuration of a tool. Here you will define values that will be used and parsed out of the user configuration file. Typically in the `config.py` module you will define static variables, static functions related to the tool, and handle data parsing. This is also where you should validate values coming in from the user configuration file that relates to your specific tool. LQMT's `tool` class, which is extended in tool's configuration modules, has a native validation method. You can use this by invoking `self.validation()`. The validation method has the following parameters(Note: bolded items are required):
- validation(**value**, **expected_type**, required, default)
    - **value**: The value you are looking to extract from the user configuration file.
    - **expected_type**: What type you expect the extracted value to be.
    - required: A boolean value to indicate whether this is a required configuration value or not. If you set this to True and the user fails to provide it in the user configuration, an error is thrown and LQMT ceases to run.
    - default: A value you provide to act as a default configuration variable. If the user fails to provide a configuration value, then the value you provide here is used instead. 

A good example to look in relation to `config.py` in the current code base would be the [to_syslog](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/tools/to_syslog/config.py) tool. An sample of this code is provided below, along with a user configuration file, to show how a `config.py` module could be setup and how to use the validation() method. 

#### Example of config.py module for the to_syslog tool
```python
class SysLogConfig(ToolConfig):
    def __init__(self, configData, csvToolInfo, unhandledCSV):
        super().__init__(configData, csvToolInfo, unhandledCSV)
        self.logger = logging.getLogger("LQMT.SysLog.{0}".format(self.getName()))

        self.host = self.validation('host', str, required=True)
        self.port = self.validation('port', int, default=514)
        self.protocol = self.validation('protocol', str, default="tcp")
        self.messageHead = self.validation('messageHead', str, required=True)
        self.messageFields = self.validation('messageFields', list, required=True)
```
#### Example of a user configuration for the to_syslog tool. 
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

The `tool.py` module of a LQMT tool is, unsurprisingly, where the core functionality of a LQMT tool is developed. This is where the heavy lifting of a tool should be integrated. The `tool.py` module is also where the interaction between the core of LQMT and the tool is established, most notably in the generic `process` function, which is directly invoked by the core process of LQMT for all tools. In the example below, we see our ToSplunk tool has a relatively simple `process` function. The establishment of the API handler is taken care of in the __init__ of the tool, and then the process function is used to simple pass the alert data to a create_message function and then to the API handler.

It's worth noting again that all tools are unique. Looking at current tools in the project you will notice the design of tools varies drastically.

#### Example of tool.py module, derived from to_splunk tool
```python
class ToSplunk(Tool):
    def __init__(self, config):
        """
        ToSplunk tool. Used to push data to Splunk using Splunk web API.

        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('All')])
        self._logger = logging.getLogger("LQMT.ToSplunk.{0}".format(self.getName()))
        self._splunk_token = ""

        if self._config.cert_check is False:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

        self.handler = ApiHandler(
            self._config.host,
            self._config.port,
            self._config.username,
            self._config.password,
            cert_check=self._config.cert_check,
            source=self._config.source,
            sourcetype=self._config.sourcetype,
            index=self._config.index
        )

    def initialize(self):
        super().initialize()

    def process(self, alert):
        """
        Process function. Handles the processing of data for the tool. 
        """
        self.handler.send_message(create_message(alert))

    def cleanup(self):
        self.handler.__exit__()
```

### Systemconfig.py
*Located under [LQMToolset/lqmt/lqm/](https://github.com/anl-cyberscience/LQMToolset/blob/master/lqmt/lqm/)*

`systemconfig.py` is where main components of LQMT are defined and accessed by LQMT's processing core; all tools that can be used by LQMT are defined here for easy access. After you finish writing your tool you need to define it in the dictionary titled `self.system_config` which is located in the `systemconfig.py` file. Below is a code template that you can use; just replace all values surrounded by asterisks(*) to match values from your tool. The sample below the template shows that that template looks like with values from the to_syslog tool filled in. 

#### Template:
```python
'*NameofTool*': {
    'module': '*toolname*', 'config_class': '*name of class(defined in config.py)*', 'tool_class': '*name of class(defined in tool.py)*'
},
```
#### Sample configuration for to_syslog
````python
'SysLog': {
    'module': 'to_syslog', 'config_class': 'SysLogConfig', 'tool_class': 'ToSysLog'
},
````
