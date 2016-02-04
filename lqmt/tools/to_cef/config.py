from lqmt.lqm.tool import ToolConfig


class CEFConfig(ToolConfig):
    def __init__(self, config, csvToolInfo, unhandledCSV):
        super().__init__(config, csvToolInfo, unhandledCSV)
        self._mapping = {}
