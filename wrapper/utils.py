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

# Deletes all fields that are not defined in outputFormat
def cleanOutput(response: dict):
    # NOTE: list() has to be used to avoid a "RuntimeError: dictionary changed size during iteration"
    for key in list(response.keys()):
        if not key in outputFormat.keys():
            del response[key]
    for record in response["records"]:
        for key in list(record.keys()):
            if not key in outputFormat["records"][0].keys():
                del record[key]
