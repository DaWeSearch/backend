"""Helper functions useful for all wrapper classes."""

import re
from typing import Callable, Optional, Union
from urllib.parse import quote_plus

from requests import exceptions, Response

from .output_format import OUTPUT_FORMAT

def get(nest: Union[dict, list, str], *args, default=None):
    """Get a value in a nested mapping/iterable.

    Args:
        nest: The object that contains nested mappings and lists.
        *args: The keys/indices.
        default: The default value for when a key does not exist or an index is out of range.
            The default value is `None`.

    Returns:
        The value at the end of the 'args-chain' in `nest` if all keys/indices
        can be accessed.
        `default` otherwise and when no args/nest is given.

    Examples:
        >>> utils.get({"foo": {"bar": [1,2,3]}}, "foo", "bar", 2)
        3
        >>> utils.get("foobar", 3)
        'b'
        >>> utils.get({"foo": [1,2,3]}, "bar", default=-1)
        -1
        >>> utils.get([1,2,3], 4, default=-1)
        -1
        >>> utils.get({"foo": {"bar": [1,2,3]}}, default=-1)
        -1
    """
    if not nest or not args:
        return default
    try:
        for arg in args:
            nest = nest[arg]
    except (TypeError, IndexError, KeyError):
        return default
    else:
        return nest

def build_group(items: [str], match: str, match_pad: str = " ", negater: str = "NOT ") -> str:
    """Build and return a search group by inserting <match> between each of the items.

    Args:
        items: List of items that should be connected.
        match: The connection between the items. Has to be one of ["AND", "OR", "NOT"].
            When using "NOT", the items are connected with "OR" and then negated.
        match_pad: The padding characters around match.
        negater: The characters that are used to negate a group.

    Returns:
        The created search group.

    Raises:
        ValueError: When given match is unknown.

    Examples:
        >>> print(build_group(["foo", "bar", "baz"], "AND", match_pad="_"))
        (foo_AND_bar_AND_baz)
        >>> print(build_group(["foo", "bar", "baz"], "NOT", negater="-"))
        -(foo OR bar OR baz)
    """
    if match not in ["AND", "OR", "NOT"]:
        raise ValueError("Unknown match.")

    group = "("

    # connect with OR and negate group
    if match == "NOT":
        group = negater + group
        match = "OR"

    # Insert and combine
    group += (match_pad + match + match_pad).join(items)

    group += ")"
    return group

def clean_output(out: dict, format_dict: dict = OUTPUT_FORMAT):
    """Delete undefined fields in the return JSON.

    Args:
        out: The returned JSON.
        format_dict: Override the output format
    """
    # NOTE: list() has to be used to avoid a:
    # "RuntimeError: dictionary changed size during iteration"
    for key in list(out.keys()):
        if key not in format_dict.keys():
            del out[key]

def invalid_output(
        query: dict, db_query: Union[str, dict], api_key: str, error: str, start_record: int,
        page_length: int) -> dict:
    """Create and return the output for a failed request.

    Args:
        query: The query in format as defined in wrapper/input_format.py.
        db_query: The query that was sent to the API in its language.
        api_key: The key used for the request.
        error: The error message returned.
        start_record: The index of the first record requested.
        page_length: The page length requested.

    Returns:
        A dict containing the passed values and "-1" as index where necessary
        to be compliant with wrapper/output_format.
    """
    out = dict()
    out["query"] = query
    out["dbQuery"] = db_query
    out["apiKey"] = api_key
    out["error"] = error
    out["result"] = {
        "total": "-1",
        "start": str(start_record),
        "pageLength": str(page_length),
        "recordsDisplayed": "0",
    }
    out["records"] = list()

    return out

def request_error_handling(req_func: Callable[..., Response], req_kwargs: dict, max_retries: int,
                           invalid: dict) -> Optional[Response]:
    """Make an HTTP request and handle error that possibly occur.

    Args:
        req_func: The function that makes the HTTP request.
            For example `requests.put`.
        req_kwargs: The arguments that will be unpacked and passed to `req_func`.
        invalid: A dictionary conforming to wrapper/output_format.py. It will be modified if an
            error occurs ("error" field will be set).

    Returns:
        If no errors occur, the return of `req_func` will be returned. Otherwise `None` will be
        returned and `invalid` modified.
    """
    for i in range(max_retries + 1):
        try:
            response = req_func(**req_kwargs)
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
            if i < max_retries:
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

def translate_get_query(query: dict, match_pad: str, negater: str, connector: str, before_groups=True) -> str:
    """Translate a GET query.

    Translate a query in format `wrapper/input_format.py` into a string that can
    be used in the query part of the url of GET requests.

    Args:
        query: The query complying to `wrapper/input_format.py`. This is modified.
        match_pad: The padding around the match values.
        negater: The negater used for negating a search group.
        conn: The connector between the different parameters.
        before_groups: Flag if the search keys should be placed before the groups
            or before every search term. Default is groups.

    Returns:
        The translated query.
    """
    # Deep copy is necessary here since we url encode the search terms
    groups = query.get("search_groups", [])
    for i in range(len(groups)):
        if groups[i].get("match") == "NOT" and query["match"] == "OR":
            raise ValueError("Only AND NOT supported.")
        for j in range(len(groups[i].get("search_terms", []))):
            term = groups[i].get("search_terms")[j]

            # Enclose search term in quotes if it contains a space and is not
            # quoted already to prevent splitting.
            if " " in term:
                if term[0] != '"':
                    term = '"' + term
                if term[-1] != '"':
                    term += '"'

            # Urlencode search term
            term = quote_plus(term)

            if not before_groups:
                new_term = "("
                for field in query.get("fields") or []:
                    new_term += field + term + connector
                term = new_term[:-len(connector)] + ")"

            groups[i].get("search_terms")[j] = term

        groups[i] = build_group(
            groups[i].get("search_terms", []), groups[i].get("match"), match_pad, negater
        )
    search_terms = build_group(groups, query.get("match"), match_pad, negater)
    query_str = ""
    if before_groups:
        for field in query.get("fields") or []:
            query_str += field + search_terms + connector
        query_str = query_str[:-len(connector)]
    else:
        query_str = search_terms
    return query_str

def build_get_query(params: dict, delim: str, connector: str) -> str:
    """Build a manual GET query from set parameters.

    Build a string that can be used in the query part of the url of a GET
    request from a dictionary containing the search parameters.

    Args:
        params: Dictionary of key, value pairs.
        delim: Delimiter between key and value.
        connector: Connector between different pairs.

    Returns:
        Built query.
    """
    url = ""
    for key, value in params.items():
        # Enclose value in quotes if it contains a space and is not quoted
        # already to prevent splitting.
        if " " in value:
            if value[0] != '"':
                value = '"' + value
            if value[-1] != '"':
                value += '"'

        # Url encode and add key value pair
        url += key + delim + quote_plus(value) + connector

    # Remove trailing connector and return
    return url[:-len(connector)]

# List of stopwords bases on (added did)
# http://ir.dcs.gla.ac.uk/resources/linguistic_utils/stop_words
STOP_WORDS = [
    'a', 'about', 'above', 'across', 'after', 'afterwards', 'again', 'against',
    'all', 'almost', 'alone', 'along', 'already', 'also', 'although', 'always',
    'am', 'among', 'amongst', 'amoungst', 'amount', 'an', 'and', 'another',
    'any', 'anyhow', 'anyone', 'anything', 'anyway', 'anywhere', 'are',
    'around', 'as', 'at', 'back', 'be', 'became', 'because', 'become',
    'becomes', 'becoming', 'been', 'before', 'beforehand', 'behind', 'being',
    'below', 'beside', 'besides', 'between', 'beyond', 'bill', 'both', 'bottom',
    'but', 'by', 'call', 'can', 'cannot', 'cant', 'co', 'computer', 'con',
    'could', 'couldnt', 'cry', 'de', 'describe', 'detail', 'did', 'do', 'done',
    'down', 'due', 'during', 'each', 'eg', 'eight', 'either', 'eleven', 'else',
    'elsewhere', 'empty', 'enough', 'etc', 'even', 'ever', 'every', 'everyone',
    'everything', 'everywhere', 'except', 'few', 'fifteen', 'fify', 'fill',
    'find', 'fire', 'first', 'five', 'for', 'former', 'formerly', 'forty',
    'found', 'four', 'from', 'front', 'full', 'further', 'get', 'give', 'go',
    'had', 'has', 'hasnt', 'have', 'he', 'hence', 'her', 'here', 'hereafter',
    'hereby', 'herein', 'hereupon', 'hers', 'herself', 'him', 'himself', 'his',
    'how', 'however', 'hundred', 'i', 'ie', 'if', 'in', 'inc', 'indeed',
    'interest', 'into', 'is', 'it', 'its', 'itself', 'keep', 'last', 'latter',
    'latterly', 'least', 'less', 'ltd', 'made', 'many', 'may', 'me',
    'meanwhile', 'might', 'mill', 'mine', 'more', 'moreover', 'most', 'mostly',
    'move', 'much', 'must', 'my', 'myself', 'name', 'namely', 'neither',
    'never', 'nevertheless', 'next', 'nine', 'no', 'nobody', 'none', 'noone',
    'nor', 'not', 'nothing', 'now', 'nowhere', 'of', 'off', 'often', 'on',
    'once', 'one', 'only', 'onto', 'or', 'other', 'others', 'otherwise', 'our',
    'ours', 'ourselves', 'out', 'over', 'own', 'part', 'per', 'perhaps',
    'please', 'put', 'rather', 're', 'same', 'see', 'seem', 'seemed', 'seeming',
    'seems', 'serious', 'several', 'she', 'should', 'show', 'side', 'since',
    'sincere', 'six', 'sixty', 'so', 'some', 'somehow', 'someone', 'something',
    'sometime', 'sometimes', 'somewhere', 'still', 'such', 'system', 'take',
    'ten', 'than', 'that', 'the', 'their', 'them', 'themselves', 'then',
    'thence', 'there', 'thereafter', 'thereby', 'therefore', 'therein',
    'thereupon', 'these', 'they', 'thick', 'thin', 'third', 'this', 'those',
    'though', 'three', 'through', 'throughout', 'thru', 'thus', 'to',
    'together', 'too', 'top', 'toward', 'towards', 'twelve', 'twenty', 'two',
    'un', 'under', 'until', 'up', 'upon', 'us', 'very', 'via', 'was', 'we',
    'well', 'were', 'what', 'whatever', 'when', 'whence', 'whenever', 'where',
    'whereafter', 'whereas', 'whereby', 'wherein', 'whereupon', 'wherever',
    'whether', 'which', 'while', 'whither', 'who', 'whoever', 'whole', 'whom',
    'whose', 'why', 'will', 'with', 'within', 'without', 'would', 'yet', 'you',
    'your', 'yours', 'yourself', 'yourselves',
]

def into_keywords_format(keywords: dict) -> list:
    """Convert a dictionary of keyword, counter pairs into a list of dicts.

    Args:
        keywords: A dictionary that contains a counter for every keyword.

    Returns:
        The keywords in the format specified in wrapper/output_format.py.
    """
    keywords_list = []
    for word, count in keywords.items():
        keywords_list.append({
            "text": word,
            "value": count,
        })
    return keywords_list

def from_keywords_format(keywords: list) -> dict:
    """Convert a list of keywords in a specific format into a dictionary.

    Args:
        keywords: A list in the format specified in wrapper/output_format.py

    Returns:
        The keywords as a dictionary with the keyword as key and its counter as
        value.
    """
    keywords_dict = {}
    for keyword in keywords:
        keywords_dict[keyword.get("text", "Unknown")] = keyword.get("value", 0)
    return keywords_dict

def titles_to_keywords(titles: str) -> list:
    """Count words and format that data.

    Args:
        titles: A string containing all titles concatinated.

    Returns:
        A list in the format specified in ["facets"]["keywords"] in
        wrapper.output_format.py
    """

    # Delete everything except alphanumeric characters, digits and spaces,
    # convert to lowercase and then split on spaces
    pat = re.compile("[^a-zA-Z0-9 ]+")
    words = pat.sub("", titles).lower().split(" ")

    freqs = {}
    for word in words:
        # Kick out stop words
        if word in STOP_WORDS:
            continue
        # Add to counter/init if new word
        elif word not in freqs:
            freqs[word] = 1
        else:
            freqs[word] += 1

    # Convert into right format
    return into_keywords_format(freqs)

def combine_facets(facets: [dict]):
    """Combine facets.

    Combine the facet counters of different wrappers.

    Args:
        facets: List of the facets dictionaries.
            NOTE: The first element will be modified!

    Returns:
        The combined facets.
    """
    total = {
        "countries": {},
        "keywords": {},
    }

    # Save one iteration.
    if len(facets) == 0:
        return total
    total["countries"] = get(facets, 0, "countries", default={})
    total["keywords"] = from_keywords_format(get(facets, 0, "keywords", default=[]))

    # Combine the rest.
    for i in range(1, len(facets)):
        if not isinstance(facets[i], dict):
            continue
        for category in facets[i]:
            if category not in total:
                continue
            for facet in get(facets, i, category, default=[]):
                if category == "countries":
                    key = facet
                    value = get(facets, i, category, facet, default=1)
                elif category == "keywords":
                    # Bring in dict format
                    key, value = list(from_keywords_format([facet]).items())[0]
                else:
                    continue

                if key in total[category]:
                    total[category][key] += int(value)
                else:
                    total[category][key] = int(value)

    total["keywords"] = into_keywords_format(total["keywords"])
    return total