#!/usr/bin/env python3
"""The input format definition.

Every wrapper has to accept a dictionary in this format as query.
When using NOT as match for one of the search_groups, the match on the first
layer has to be AND.
When setting the fields, "all" cannot be combined with the rest but has to be
used alone.
"""

input_format = {
    "search_groups": [{
        "search_terms": ["Search terms"],
        "match": "AND|OR|NOT",
    }],
    "match": "AND|OR",
    "fields": ["all", "abstract", "keywords", "title"],
}
