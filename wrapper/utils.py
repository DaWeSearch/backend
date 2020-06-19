#!/usr/bin/env python3

from typing import Union

from .outputFormat import outputFormat

def buildGroup(items: [str], match: str, matchPad: str = " ", negater: str = "NOT ") -> str:
    """Build and return a search group by inserting <match> between each of the items.

    Args:
        items: List of items that should be connected.
        match: The connection between the items. Has to be one of ["AND", "OR", "NOT"].
            When using "NOT", the items are connected with "OR" and then negated.
        matchPad: The padding characters around match.
        negater: The characters that are used to negate a group.

    Returns:
        The created search group.

    Examples:
        >>> print(buildGroup(["foo", "bar", "baz"], "AND", matchPad="_"))
        (foo_AND_bar_AND_baz)
        >>> print(buildGroup(["foo", "bar", "baz"], "NOT", negater="-"))
        -(foo OR bar OR baz)
    """
    assert match in ["AND", "OR", "NOT"]

    group = "("

    # connect with OR and negate group
    if match == "NOT":
        group = negater + group
        match = "OR"

    # Insert and combine
    group += (matchPad + match + matchPad).join(items)

    group += ")"
    return group

def cleanOutput(out: dict, formatDict: dict = outputFormat):
    """Delete undefined fields in the return JSON.

    Args:
        out: The returned JSON.
        formatDict: Override the output format
    """
    # NOTE: list() has to be used to avoid a "RuntimeError: dictionary changed size during iteration"
    for key in list(out.keys()):
        if key not in formatDict.keys():
            del out[key]

def invalidOutput(
        query: dict, dbQuery: Union[str, dict], apiKey: str, error: str, startRecord: int,
        pageLength: int) -> dict:
    """Create and return the output for a failed request.

    Args:
        query: The query in format as defined in wrapper/inputFormat.py.
        dbQuery: The query that was sent to the API in its language.
        apiKey: The key used for the request.
        error: The error message returned.
        startRecord: The index of the first record requested.
        pageLength: The page length requested.

    Returns:
        A dict containing the passed values and "-1" as index where necessary
        to be compliant with wrapper/outputFormat.
    """
    out = dict()
    out["query"] = query
    out["dbQuery"] = dbQuery
    out["apiKey"] = apiKey
    out["error"] = error
    out["result"] = {
        "total": "-1",
        "start": str(startRecord),
        "pageLength": str(pageLength),
        "recordsDisplayed": "-1",
    }
    out["records"] = list()

    return out
