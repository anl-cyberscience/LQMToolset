class Error(Exception):
    """Base class for exceptions"""
    pass


class ConfigurationError(Error):
    """An exception representing that there was an error in configuring an item"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AuthenticationError(Error):
    """An exception representing that there was an error during an authentication process"""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
