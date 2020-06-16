#!/usr/bin/env python3

from typing import Union

from .outputFormat import outputFormat

def buildGroup(items: [str], match: str, matchPad: str = " ", negater: str = "NOT ") -> str:
    """Build and return a search group by inserting <match> between each of the items."""
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
    """Delete undefined fields in the return JSON."""
    # NOTE: list() has to be used to avoid a "RuntimeError: dictionary changed size during iteration"
    for key in list(out.keys()):
        if key not in formatDict.keys():
            del out[key]

def invalidOutput(
        query: dict, dbQuery: Union[str, dict], apiKey: str, error: str, startRecord: int,
        pageLength: int) -> dict:
    """Create and return the output for a failed request."""
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
