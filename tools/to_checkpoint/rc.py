import re

_valid_varnames = set([
    'hostname',
    'port',
    'username',
    'originator',
    ])

class CheckpointRC():
    def __init__(self, rcfile):
        self.cprc=self._load_file(rcfile)
        
    def _load_file(self,rcfile):
        try:
            f = open(rcfile, 'r')
        except IOError as msg:
            return None

        cprc = {}
        for line in f:
            line = line.rstrip('\r\n')
            if re.search(r'(^#|^\s*$)', line):
                continue
            result = re.search(r'\s*(\w+)\s*=\s*(.+)', line)
            if (result and result.group(1) in _valid_varnames):
                cprc[result.group(1)] = result.group(2)

        f.close()

        return cprc
