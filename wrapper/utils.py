#!/usr/bin/env python3

from .outputFormat import outputFormat

# Builds a search group by inserting match between the seach terms
def buildGroup(items: [str], match: str, matchPad: str = " ", negater: str = "NOT ") -> str:
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

# Deletes undefined fields
def cleanOutput(out: dict, formatDict: dict = outputFormat):
    # NOTE: list() has to be used to avoid a "RuntimeError: dictionary changed size during iteration"
    for key in list(out.keys()):
        if not key in formatDict.keys():
            del out[key]