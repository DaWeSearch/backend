#!/usr/bin/env python3

from copy import deepcopy
from collections.abc import Mapping
from typing import Callable, Optional, Union
import urllib.parse

from requests import exceptions, Response

from .outputFormat import outputFormat

def get(dictionary: dict, *args, default=None):
    """Get a value in a nested mapping.

    Args:
        dictionary: The dictionary.
        *args: The keys.
        default: The default value if a key does not exist on the way.
                 Be careful with dictionary as those are further accessed. (see last example)

    Returns:
        If `dictionary` is a mapping, `*args` were specified and every key exists:
        The value at the end is returned.
        Otherwise `default` is returned.

    Examples:
        >>> utils.get({"foo": {"bar": [1,2,3]}}, "foo", "bar")
        [1, 2, 3]
        >>> utils.get({"foo": {"bar": [1,2,3]}}, default=3)
        3
        >>> utils.get("foobar", "foo", "bar", default=3)
        3
        >>> utils.get({"foo": {"bar": [1,2,2]}}, "foo", "bar", "baz", default=3)
        3
        >>> utils.get(f, "oof", "bar", default={"bar": [1,2,3]})
        [1, 2, 3]
    """
    if not dictionary or not args:
        return default
    for arg in args:
        if not isinstance(dictionary, Mapping):
            return default
        dictionary = dictionary.get(arg, default)

    return dictionary

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
        "recordsDisplayed": "0",
    }
    out["records"] = list()

    return out

def requestErrorHandling(reqFunc: Callable[..., Response], reqKwargs: dict, maxRetries: int,
        invalid: dict) -> Optional[Response]:
    """Make an HTTP request and handle error that possibly occur.

    Args:
        reqFunc: The function that makes the HTTP request.
            For example `requests.put`.
        reqKwargs: The arguments that will be unpacked and passed to `reqFunc`.
        invalid: A dictionary conforming to wrapper/outputFormat.py. It will be modified if an
            error occurs ("error" field will be set).

    Returns:
        If no errors occur, the return of `reqFunc` will be returned. Othewise `None` will be
        returned and `invalid` modified.
    """
    for i in range(maxRetries + 1):
        try:
            response = reqFunc(**reqKwargs)
            # Raise an HTTP error if there were any
            response.raise_for_status()
        except exceptions.HTTPError as err:
            invalid["error"] = "HTTP error: " + str(err)
            return None
        except exceptions.ConnectionError as err:
            invalid["error"] = "Connection error: Failed to establish a connection: " \
                "Name or service not known."
            return None
        except exceptions.Timeout as err:
            if i < maxRetries:
                # Try again
                continue
            # Too many failed attempts
            invalid["error"] = "Connection error: Failed to establish a connection: Timeout."
            return None
        except exceptions.RequestException as err:
            invalid["error"] = "Request error: " + str(err)
            return None

        # request successful
        break
    return response

def translateGetQuery(query: dict, matchPad: str, negater: str) -> str:
    # Deep copy is necessary here since we url encode the search terms
    groups = deepcopy(query.get("search_groups", []))
    for i in range(len(groups)):
        if groups[i].get("match") == "NOT" and query["match"] == "OR":
            raise ValueError("Only AND NOT supported.")
        for j in range(len(groups[i].get("search_terms", []))):
            term = groups[i].get("search_terms")[j]

            # Enclose search term in quotes if it contains a space to prevent splitting.
            if " " in term:
                term = '"' + term + '"'

            # Urlencode search term
            groups[i].get("search_terms")[j] = urllib.parse.quote_plus(term)

        groups[i] = buildGroup(
            groups[i].get("search_terms", []), groups[i].get("match"), matchPad, negater
        )
    return buildGroup(groups, query.get("match"), matchPad, negater)
