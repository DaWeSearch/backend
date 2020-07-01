#!/usr/bin/env python3
"""The input format definition.

Every wrapper has to accept a dictionary in this format as query.
"""

inputFormat = {
	"search_groups": [{
		"search_terms": ["Search terms"],
		"match": "AND|OR|NOT",
	}],
	"match": "AND|OR",
	"parameters": ["all", "title", "keywords"],
}
