"""Various Free Range Routing (FRR) utilities."""

# Project
from hyperglass_agent.log import log
from hyperglass_agent.constants import AFI_DISPLAY_MAP


async def parse_frr_output(raw, query_data, not_found):
    """Parse raw CLI output from FRR (vtysh) and return parsed output.

    Arguments:
        raw {str} -- Raw output from vtysh
        query_data {object} -- Validated query object
        not_found {str} -- Lookup not found message template

    Returns:
        {str} -- Parsed output
    """
    raw_split = raw.strip()
    if not raw_split:
        notfound_message = not_found.format(
            target=query_data.target, afi=AFI_DISPLAY_MAP[query_data.afi]
        )
        output = notfound_message
    else:
        output = raw_split

    log.debug(f"Parsed output:\n{output}")
    return output
