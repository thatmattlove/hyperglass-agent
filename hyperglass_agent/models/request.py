"""Validate the raw JSON request data."""

# Standard Library
from typing import Union, Optional

# Third Party
from pydantic import BaseModel, StrictStr, IPvAnyAddress, validator

# Project
from hyperglass_agent.constants import SUPPORTED_QUERY
from hyperglass_agent.exceptions import QueryError
from hyperglass_agent.models._utils import StrictBytes


class Request(BaseModel):
    """Validate and serialize raw request."""

    query_type: str
    vrf: str
    afi: str
    source: Optional[IPvAnyAddress]
    target: str

    @validator("query_type")
    def validate_query_type(cls, value):  # noqa: N805
        """Pydantic validator: validate that query type is supported.

        Raises:
            QueryError: Raised if the received query type is not supported.

        Returns:
            {str} -- Set query_type attribute if valid.
        """
        if value not in SUPPORTED_QUERY:
            raise QueryError("Query Type '{query_type}' is Invalid", query_type=value)
        return value


class EncodedRequest(BaseModel):
    """Validate encoded request."""

    encoded: Union[StrictStr, StrictBytes]
