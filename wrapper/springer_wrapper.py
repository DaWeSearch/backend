#!/usr/bin/env python3
"""A wrapper for the Springer Nature API."""

from copy import deepcopy
from typing import Optional

import requests

from . import utils
from .output_format import output_format
from .wrapper_interface import WrapperInterface

class SpringerWrapper(WrapperInterface):
    """A wrapper class for the Springer Nature API."""

    def __init__(self, apiKey: str):
        """Initialize a wrapper object.

        Args:
            apiKey: The API key that should be used for a request.
        """
        self.apiKey = apiKey

        self.__resultFormat = "json"

        self.__collection = "metadata"

        self.__startRecord = 1

        self.__numRecords = 50

        self.__parameters = {}

        self.__maxRetries = 3

    @property
    def endpoint(self) -> str:
        """Return the endpoint used for the query."""
        return "http://api.springernature.com"

    @property
    def allowedResultFormats(self) -> {str: [str]}:
        """Return a dictionary that contains the available result formats for each collection."""
        return {
            "meta/v2": ["pam", "jats", "json", "jsonp", "jsonld"],
            "metadata": ["pam", "json", "jsonp"],
            "openaccess": ["jats", "json", "jsonp"],
            "integro": ["xml"]
        }

    @property
    def resultFormat(self) -> str:
        """Return the result format that will be used for the query."""
        return self.__resultFormat

    @resultFormat.setter
    def resultFormat(self, value: str):
        """Set the result format.

        Args:
            value: The result format that will be set. Has to be allowed for set collection.
        """
        # Strip leading and trailing whitespace and convert to lower case
        value = str(value).strip().lower()

        # Check if the format is supported by the selected collection
        if value in self.allowedResultFormats[self.collection]:
            self.__resultFormat = value
        else:
            raise ValueError(f"Illegal format {value} for collection {self.collection}")

    @property
    def collection(self) -> str:
        """Return the collection in which the query searches."""
        return self.__collection

    @collection.setter
    def collection(self, value: str):
        """Set the collection used.

        Args:
            value: The collection that will be set. Has to be an allowed value.
        """
        # Strip leading and trailing whitespace and convert to lower case
        value = str(value).strip().lower()

        if value not in self.allowedResultFormats:
            raise ValueError(f"Unknown collection {value}")

        # Adjust resultFormat
        if self.resultFormat not in self.allowedResultFormats[value]:
            self.resultFormat = self.allowedResultFormats[value][0]
            print(f"Illegal resultFormat for collection. Setting to {self.resultFormat}")

        self.__collection = value

    @property
    def maxRecords(self) -> int:
        """Return the maximum number of results that the API can return."""
        if self.collection == "openaccess":
            return 20

        return 50

    @property
    def showNum(self) -> int:
        """Return the number of results that the API will return."""
        return self.__numRecords

    @showNum.setter
    def showNum(self, value: int):
        """Set the number of results that will be returned.

        Args:
            value: The number of results.
        """
        if value > self.maxRecords:
            print(f"{value} exceeds maximum of {self.maxRecords}. Set to maximum.")
            self.__numRecords = self.maxRecords
        else:
            self.__numRecords = value

    @property
    def allowedSearchFields(self) -> {str: [str]}:
        """Return all allowed search parameter, value combination.

        An empty array means no restrictions for the value of that key.
        """
        return {
            "doi":[], "subject":[], "keyword":[], "pub":[], "year":[],
            "onlinedate":[], "onlinedatefrom":[], "onlinedateto": [],
            "country":[], "isbn":[], "issn":[], "journalid":[],
            "topicalcollection":[], "journalonlinefirst":["true"],
            "date":[], "issuetype":[], "issue":[], "volume":[],
            "type":["Journal", "Book"], "openaccess":["true"], "title": [],
            "orgname": [], "journal": [], "book": [], "name": []
        }

    @property
    def maxRetries(self) -> int:
        """Return the maximum number of retries the wrapper will do on a timeout."""
        return self.__maxRetries

    @maxRetries.setter
    def maxRetries(self, value: int):
        """Set maximum number of retries on a timeout.

        Args:
            value: Number of retries that will be set.
        """
        self.__maxRetries = value

    @property
    def fieldsTranslateMap(self) -> dict:
        """Return the translate map for the fields field of the input format."""
        return {
            "all": "", "keywords": "keyword", "title": "title"
        }

    def searchField(self, key: str, value):
        """Set the value for a given search parameter in a manual search.

        Args:
            key: The search parameter.
            value: The value that the search parameter should have.
        """
        # Convert to lowercase and strip leading and trailing whitespace
        key = str(key).strip().lower()
        value = str(value).strip()
        if len(value) == 0:
            raise ValueError(f"Value is empty")

        # Check if key and value are allowed as combination
        if key in self.allowedSearchFields:
            if len(self.allowedSearchFields[key]) == 0 or value in self.allowedSearchFields[key]:
                self.__parameters[key] = value
            else:
                raise ValueError(f"Illegal value {value} for search-field {key}")
        else:
            raise ValueError(f"Searches against {key} are not supported")

    def resetAllFields(self):
        """Reset all search parameters"""
        self.__parameters = {}

    def resetField(self, key: str):
        """Reset a search parameter.

        Args:
            key: The search parameter that shall be resetted.
        """
        if key in self.__parameters:
            del self.__parameters[key]
        else:
            raise ValueError(f"Field {key} is not set.")

    def queryPrefix(self) -> str:
        """Build and return the API query url without the actual search terms."""
        url = self.endpoint
        url += "/" + str(self.collection)
        url += "/" + str(self.resultFormat)
        url += "?api_key=" + str(self.apiKey)
        url += "&s=" + str(self.__startRecord)
        url += "&p=" + str(self.showNum)

        return url

    def buildQuery(self) -> str:
        """Build and return a manual search from the values specified by searchField."""
        if len(self.__parameters) == 0:
            raise ValueError("No search-parameters set.")

        url = self.queryPrefix()
        url += "&q="
        url += utils.buildGetQuery(self.__parameters, ":", "+")
        return url

    def translateQuery(self, query: dict) -> str:
        """Translate a dictionary into a query that the API understands.

        Args:
            query: A query dictionary as defined in wrapper/input_format.py.
        """
        url = self.queryPrefix()
        url += "&q="


        # Copy the query since we will modify it.
        query = deepcopy(query)


        # Check if fields were given.
        if len(query.get("fields", [])) == 0:
            query["fields"] = list(self.fieldsTranslateMap.keys())[:1]
            print(f"No search fields specified. Using default {query['fields'][0]}.")
        # "Translate" the given field names to search in.
        for i in range(len(query["fields"])):
            field = query["fields"][i]
            if field in self.fieldsTranslateMap:
                query["fields"][i] = self.fieldsTranslateMap.get(field) + ":"
                # Empty key for "all"
                if query["fields"][i] == ":":
                    query["fields"][i] = ""
            else:
                raise ValueError(f"Searching against field {field} is not supported.")

        url += utils.translateGetQuery(query, "+", "-", "+OR+")
        return url

    def startAt(self, value: int):
        """Set the index from which the returned results start.

        Args:
            value: The start index.
        """
        self.__startRecord = int(value)

    def formatResponse(self, response: requests.Response, query: dict):
        """Return the formatted response as defined in wrapper/output_format.py.

        Args:
            response: The requests response returned by `callAPI`.
            query: The query dict used as defined in wrapper/input_format.py.

        Returns:
            The formatted response.
        """
        if self.resultFormat == "json" or self.resultFormat == "jsonld":
            # Load into dict
            response = response.json()

            # Modify response to fit the defined wrapper output format
            response["dbQuery"] = response.get("query", {})
            response["query"] = query
            if ("result" in response) and (len(response["result"]) > 0):
                response["result"] = response.pop("result")[0]
            else:
                response["result"] = {
                    "total": -1,
                    "start": -1,
                    "pageLength": -1,
                    "recordsDisplayed": len(response.get("records", [])),
                }
            for record in response.get("records") or []:
                if ("url" in record) and (len(record["url"]) > 0) and ("value" in record["url"][0]):
                    record["uri"] = record["url"][0]["value"]
                authors = []
                for author in record.get("creators") or []:
                    authors.append(author["creator"])
                record["authors"] = authors
                record["pages"] = {
                    "first": record.get("startingPage"),
                    "last": record.get("endingPage"),
                }
                if self.collection == "openaccess":
                    record["openAccess"] = True
                elif "openaccess" in record:
                    record["openAccess"] = (record.pop("openaccess") == "true")

                # Delete all undefined fields
                utils.cleanOutput(record, output_format["records"][0])

            # Delete all undefined fields
            utils.cleanOutput(response)

            return response

        else:
            print(f"No formatter defined for {self.resultFormat}. Returning raw response.")
            return response.text

    def callAPI(self, query: Optional[dict] = None, raw: bool = False, dry: bool = False):
        """Make the call to the API.

        If no query is given build the manual search specified by searchField() calls.

        Args:
            query: A dictionary as defined in wrapper/input_format.py.
                If not specified, the parameters dict modified by searchField is used.
            raw: Should the raw request.Response of the query be returned?
            dry: Should only the data for the API request be returned and nothing executed?

        Returns:
            If dry is True a tuple is returned containing query-url, request-headers and -body in
                this order. This wrapper class will never return headers and a body but `None`
                instead.
            If raw is False the formatted response is returned else the raw request.Response.
        """
        if not query:
            url = self.buildQuery()
        else:
            url = self.translateQuery(query)

        if dry:
            return url, None, None

        # Make the request and handle errors
        invalid = utils.invalidOutput(
            query, url.split("&q=")[-1], self.apiKey, "", self.__startRecord, self.showNum
        )
        response = utils.requestErrorHandling(requests.get, {"url": url}, self.maxRetries, invalid)
        if response is None:
            print(invalid["error"])
            return invalid
        if raw:
            return response
        return self.formatResponse(response, query)
