#!/usr/bin/env python3
"""The output format definition.

Every wrapper has to return a dictionary in this format when called.
"""

OUTPUT_FORMAT = {
    "query": "The query provided by the front-end",
    "dbQuery": "The query that was sent to the database server",
    "apiKey": "The API key used for the query",
    "error": "If there was one: error description",
    "result": {
        "total": "Total amount of hits in the DB",
        "start": "Index at which the returned results start",
        "pageLength": "Number of results per page requested",
        "recordsDisplayed": "Number of records this exact query returned",
    },
    "records": [{
        "contentType": "Type of the content (e.g. Article)",
        "title": "The title of the record",
        "authors": ["Full name of one creator"],
        "publicationName": "Name of the publication",
        "openAccess": "Bool: Belongs to openaccess collection",
        "doi": "The DOI of the record",
        "publisher": "Name of the publisher",
        "publicationDate": "Date of publication",
        "publicationType": "Type of publication",
        "issn": "International Standard Serial Number",
        "volume": "Volume of the publication",
        "number": "Number of the publication",
        "genre": ["Name of one genre"],
        "pages": {
            "first": "First page in publication",
            "last": "Last page in publication",
        },
        "journalId": "ID of the publication journal",
        "copyright": "Copyright notice",
        "abstract": "Abstract (Summary)",
        "uri": "Link to the record",
    }],
}
