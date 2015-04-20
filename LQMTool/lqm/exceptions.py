


class ConfigurationError(Exception):
    """An exception representing that there was an error in configuring an item"""
    def __init__(self, value):
        self.value=value
    def __str__(self):
        return repr(self.value)

