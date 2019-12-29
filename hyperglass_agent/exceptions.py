"""Module specific exception classes."""

# Standard Library Imports
import json as _json

# Project Imports
from hyperglass_agent.util import log


class HyperglassAgentError(Exception):
    """Base exception class for all hyperglass-agent errors."""

    def __init__(self, message="", code=500, keywords=None):
        """Initialize the app's base exception class.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            code {int} -- HTTP Status Code (default: {500})
            keywords {[type]} -- 'Important' keywords (default: {None})
        """
        self.message = message
        self.code = code
        self.keywords = keywords or []
        log.critical(self.__repr__())

    def __str__(self):
        """Return the instance's error message.

        Returns:
            {str} -- Error Message
        """
        return self.message

    def __repr__(self):
        """Return the instance's code & error message in a string.

        Returns:
            {str} -- Error message with code
        """
        return f"{self.code}: {self.message}"

    def __dict__(self):
        """Return the instance's attributes as a dictionary.

        Returns:
            {dict} -- Exception attributes in dict
        """
        return {"message": self.message, "code": self.code, "keywords": self.keywords}

    def json(self):
        """Return the instance's attributes as a JSON object.

        Returns:
            {str} -- Exception attributes as JSON
        """
        return _json.dumps(
            {"message": self.message, "code": self.code, "keywords": self.keywords}
        )

    @property
    def code(self):
        """Return the instance's `code` attribute.

        Returns:
            {int} -- HTTP Status Code
        """
        return self.code

    @property
    def message(self):
        """Return the instance's `message` attribute.

        Returns:
            {str} -- Error Message
        """
        return self.message

    @property
    def keywords(self):
        """Return the instance's `keywords` attribute.

        Returns:
            {list} -- Keywords List
        """
        return self.keywords


class ConfigInvalid(HyperglassAgentError):
    """Raised when a config item fails type or option validation."""

    def __init__(self, **kwargs):
        """Format a pre-defined message with passed keyword arguments."""
        self.message = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self.keywords = list(kwargs.values())
        super().__init__(message=self.message, keywords=self.keywords)


class _FmtHyperglassAgentError(HyperglassAgentError):
    def __init__(self, unformatted_msg, **kwargs):
        self.message = unformatted_msg.format(**kwargs)
        self.keywords = list(kwargs.values())
        super().__init__(message=self.message, keywords=self.keywords)


class ConfigError(_FmtHyperglassAgentError):
    """Raised for generic user-config issues."""


class QueryError(_FmtHyperglassAgentError):
    """Raised when a received query is invalid according to the query model."""

    code = 400


class ExecutionError(_FmtHyperglassAgentError):
    """Raised when an error occurs during shell command execution."""

    code = 503


class SecurityError(_FmtHyperglassAgentError):
    """Raised when a JWT decoding error occurs."""

    code = 500
