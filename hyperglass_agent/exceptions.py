# Project Imports


class HyperglassAgentError(Exception):
    """Base exception class for all hyperglass-agent errors"""

    def __init__(self, message="", code=500, keywords=[]):
        self.message = message
        self.code = code
        self.keywords = keywords

    def __str__(self):
        return self.message

    def __dict__(self):
        return {"message": self.message, "code": self.code, "keywords": self.keywords}


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


class QueryError(HyperglassAgentError):
    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.code = 400
        super().__init__(message=self.message, code=self.code)


class ExecutionError(HyperglassAgentError):
    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.code = 500
        super().__init__(message=self.message, code=self.code)


class SecurityError(HyperglassAgentError):
    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.code = 500
        super().__init__(message=self.message, code=self.code)
