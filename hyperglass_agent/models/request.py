# Standard Library Imports
import ipaddress
from typing import Union
from typing import Optional

# Third Party Imports
from pydantic import BaseModel
from pydantic import validator

# Project Imports
from hyperglass_agent.constants import SUPPORTED_QUERY
from hyperglass_agent.exceptions import QueryError


class Request(BaseModel):
    query_type: str
    vrf: str
    afi: str
    source: Optional[Union[ipaddress.IPv4Address, ipaddress.IPv6Address]]
    target: str

    @validator("query_type")
    def validate_query_type(cls, value):
        if value not in SUPPORTED_QUERY:
            raise QueryError("Query Type '{query_type}' is Invalid", query_type=value)
        return value
