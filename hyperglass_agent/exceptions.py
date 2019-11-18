class HyperglassAgentError(Exception):
    """Base exception class for all hyperglass-agent errors"""

    def __init__(self, message="", alert="warning", keywords=[]):
        self.message = message
        self.alert = alert
        self.keywords = keywords

    def __str__(self):
        return self.message

    def __dict__(self):
        return {"message": self.message, "alert": self.alert, "keywords": self.keywords}


class ConfigError(HyperglassAgentError):
    """Raised for generic user-config issues."""

    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)


class ConfigInvalid(HyperglassAgentError):
    """Raised when a config item fails type or option validation"""

    def __init__(self, **kwargs):
        self.message = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self.keywords = [value for value in kwargs.values()]
        super().__init__(message=self.message, keywords=self.keywords)
