from lqmt.lqm.tool import ToolConfig

class CEFConfig(ToolConfig):
    def __init__(self, config,csvToolInfo,unhandledCSV):
        ToolConfig.__init__(self, config,csvToolInfo,unhandledCSV)
        self._mapping={}
