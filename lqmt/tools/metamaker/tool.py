import logging
import os
from lqmt.lqm.tool import PullTool
from lqmt.tools.metamaker.metamaker import MetaMaker
from collections import namedtuple

class MetaMakerTool(PullTool):
    def __init__(self,config):
        super().__init__(config)
        self._logger = logging.getLogger("LQMT.MetaMaker.{0}".format(self.getName()))
        self._splunk_token = ""
        self.dir_items = ""
        self.ArgTupleTemplate = namedtuple(
            "arguments", 
            ["source_file", "format", "type", "site", "sent_time", "upload_id", 'sensitivity', 'recon', 'restrictions',
             'directory']
        )

    def initialize(self):
        super().initialize()
        self.dir_items = os.listdir(self._config.path)

    def process(self, alert):        
        # iterate through directory items
        for item in self.dir_items:
            # if first char in item is ".", skip. Dot(.) files are metadata files
            if item[0] != ".":
                if os.path.isfile(self._config.path+item):
                    mm = MetaMaker(
                        self.ArgTupleTemplate(
                            item,
                            self._config.format,
                            self._config.type,
                            self._config.site,
                            "1507914177", 
                            "N/A",
                            self._config.sensitivity,
                            self._config.recon, 
                            self._config.restrictions,
                            self._config.path
                            )
                        )
                    mm.make_meta()
                
    def commit(self):
        pass
    
    def cleanup(self):
        pass
