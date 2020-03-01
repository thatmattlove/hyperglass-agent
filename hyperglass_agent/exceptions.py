"""Module specific exception classes."""

# Third Party
# Third Party Imports
import ujson as _json

# Project
# Project Imports
from hyperglass_agent.util import log


class HyperglassAgentError(Exception):
    """Base exception class for all hyperglass-agent errors."""

    def __init__(self, message="", code=500, keywords=None):
        """Initialize the app's base exception class.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            code {int} -- HTTP Status Code (default: {500})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self._message = message
        self._code = code
        self._keywords = keywords or []
        log.critical(self.__repr__())

    def __str__(self):
        """Return the instance's error message.

        Returns:
            {str} -- Error Message
        """
        return self._message

    def __repr__(self):
        """Return the instance's code & error message in a string.

        Returns:
            {str} -- Error message with code
        """
        return f"{self._code}: {self._message}"

    def __dict__(self):
        """Return the instance's attributes as a dictionary.

        Returns:
            {dict} -- Exception attributes in dict
        """
        return {
            "message": self._message,
            "code": self._code,
            "keywords": self._keywords,
        }

    def json(self):
        """Return the instance's attributes as a JSON object.

        Returns:
            {str} -- Exception attributes as JSON
        """
        return _json.dumps(
            {"message": self._message, "code": self._code, "keywords": self._keywords}
        )

    @property
    def code(self):
        """Return the instance's `code` attribute.

        Returns:
            {int} -- HTTP Status Code
        """
        return self._code

    @property
    def message(self):
        """Return the instance's `message` attribute.

        Returns:
            {str} -- Error Message
        """
        return self._message

    @property
    def keywords(self):
        """Return the instance's `keywords` attribute.

        Returns:
            {list} -- Keywords List
        """
        return self._keywords


class ConfigInvalid(HyperglassAgentError):
    """Raised when a config item fails type or option validation."""

    def __init__(self, **kwargs):
        """Format a pre-defined message with passed keyword arguments."""
        self._message = 'The value field "{field}" is invalid: {error_msg}'.format(
            **kwargs
        )
        self._keywords = list(kwargs.values())
        super().__init__(message=self._message, keywords=self._keywords)


class _UnformattedHyperglassError(HyperglassAgentError):
    """Base exception class for freeform error messages."""

    _code = 500

    def __init__(self, unformatted_msg="undefined error", code=None, **kwargs):
        """Format error message with keyword arguments.

        Keyword Arguments:
            message {str} -- Error message (default: {""})
            alert {str} -- Error severity (default: {"warning"})
            keywords {list} -- 'Important' keywords (default: {None})
        """
        self._message = unformatted_msg.format(**kwargs)
        self._alert = code or self._code
        self._keywords = list(kwargs.values())
        super().__init__(
            message=self._message, code=self._code, keywords=self._keywords
        )


class ConfigError(_UnformattedHyperglassError):
    """Raised for generic user-config issues."""


class QueryError(_UnformattedHyperglassError):
    """Raised when a received query is invalid according to the query model."""

    _code = 400


class ExecutionError(_UnformattedHyperglassError):
    """Raised when an error occurs during shell command execution."""

    _code = 503


class SecurityError(_UnformattedHyperglassError):
    """Raised when a JWT decoding error occurs."""

    _code = 500
