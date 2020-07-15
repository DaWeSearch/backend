"""A wrapper for the Springer Nature API."""

from copy import deepcopy
from typing import Optional

import pycountry
import requests

from . import utils
from .output_format import OUTPUT_FORMAT
from .wrapper_interface import WrapperInterface

class SpringerWrapper(WrapperInterface):
    """A wrapper class for the Springer Nature API."""

    def __init__(self, api_key: str):
        """Initialize a wrapper object.

        Args:
            api_key: The API key that should be used for a request.
        """
        self.api_key = api_key

        self.__result_format = "json"

        self.__collection = "metadata"

        self.__start_record = 1

        self.__num_records = 50

        self.__parameters = {}

        self.__max_retries = 3

    @property
    def endpoint(self) -> str:
        """Return the endpoint used for the query."""
        return "http://api.springernature.com"

    @property
    def allowed_result_formats(self) -> {str: [str]}:
        """Return a dictionary that contains the available result formats for each collection."""
        return {
            "meta/v2": ["pam", "jats", "json", "jsonp", "jsonld"],
            "metadata": ["pam", "json", "jsonp"],
            "openaccess": ["jats", "json", "jsonp"],
            "integro": ["xml"]
        }

    @property
    def result_format(self) -> str:
        """Return the result format that will be used for the query."""
        return self.__result_format

    @result_format.setter
    def result_format(self, value: str):
        """Set the result format.

        Args:
            value: The result format that will be set. Has to be allowed for set collection.
        """
        # Strip leading and trailing whitespace and convert to lower case
        value = str(value).strip().lower()

        # Check if the format is supported by the selected collection
        if value in self.allowed_result_formats[self.collection]:
            self.__result_format = value
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

        if value not in self.allowed_result_formats:
            raise ValueError(f"Unknown collection {value}")

        # Adjust result_format
        if self.result_format not in self.allowed_result_formats[value]:
            self.result_format = self.allowed_result_formats[value][0]
            print(f"Illegal result_format for collection. Setting to {self.result_format}")

        self.__collection = value

    @property
    def max_records(self) -> int:
        """Return the maximum number of results that the API can return."""
        if self.collection == "openaccess":
            return 20

        return 50

    @property
    def show_num(self) -> int:
        """Return the number of results that the API will return."""
        return self.__num_records

    @show_num.setter
    def show_num(self, value: int):
        """Set the number of results that will be returned.

        Args:
            value: The number of results.
        """
        if value > self.max_records:
            print(f"{value} exceeds maximum of {self.max_records}. Set to maximum.")
            self.__num_records = self.max_records
        else:
            self.__num_records = value

    @property
    def allowed_search_fields(self) -> {str: [str]}:
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
    def max_retries(self) -> int:
        """Return the maximum number of retries the wrapper will do on a timeout."""
        return self.__max_retries

    @max_retries.setter
    def max_retries(self, value: int):
        """Set maximum number of retries on a timeout.

        Args:
            value: Number of retries that will be set.
        """
        self.__max_retries = value

    @property
    def fields_translate_map(self) -> dict:
        """Return the translate map for the fields field of the input format."""
        return {
            "all": "", "keywords": "keyword", "title": "title"
        }

    def search_field(self, key: str, value):
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
        if key in self.allowed_search_fields:
            if len(self.allowed_search_fields[key]) == 0 \
                    or value in self.allowed_search_fields[key]:
                self.__parameters[key] = value
            else:
                raise ValueError(f"Illegal value {value} for search-field {key}")
        else:
            raise ValueError(f"Searches against {key} are not supported")

    def reset_all_fields(self):
        """Reset all search parameters"""
        self.__parameters = {}

    def reset_field(self, key: str):
        """Reset a search parameter.

        Args:
            key: The search parameter that shall be resetted.
        """
        if key in self.__parameters:
            del self.__parameters[key]
        else:
            raise ValueError(f"Field {key} is not set.")

    def query_prefix(self) -> str:
        """Build and return the API query url without the actual search terms."""
        url = self.endpoint
        url += "/" + str(self.collection)
        url += "/" + str(self.result_format)
        url += "?api_key=" + str(self.api_key)
        url += "&s=" + str(self.__start_record)
        url += "&p=" + str(self.show_num)

        return url

    def build_query(self) -> str:
        """Build and return a manual search from the values specified by search_field."""
        if len(self.__parameters) == 0:
            raise ValueError("No search-parameters set.")

        url = self.query_prefix()
        url += "&q="
        url += utils.build_get_query(self.__parameters, ":", "+")
        return url

    def translate_query(self, query: dict) -> str:
        """Translate a dictionary into a query that the API understands.

        Args:
            query: A query dictionary as defined in wrapper/input_format.py.
        """
        url = self.query_prefix()
        url += "&q="


        # Copy the query since we will modify it.
        query = deepcopy(query)


        # Check if fields were given.
        if len(query.get("fields", [])) == 0:
            query["fields"] = list(self.fields_translate_map.keys())[:1]
            print(f"No search fields specified. Using default {query['fields'][0]}.")
        # "Translate" the given field names to search in.
        for i in range(len(query["fields"])):
            field = query["fields"][i]
            if field in self.fields_translate_map:
                query["fields"][i] = self.fields_translate_map.get(field) + ":"
                # Empty key for "all"
                if query["fields"][i] == ":":
                    query["fields"][i] = ""
            else:
                raise ValueError(f"Searching against field {field} is not supported.")

        url += utils.translate_get_query(query, "+", "-", "+OR+")
        return url

    def start_at(self, value: int):
        """Set the index from which the returned results start.

        Args:
            value: The start index. (1-based)
        """
        self.__start_record = int(value)

    def format_response(self, response: requests.Response, query: dict):
        """Return the formatted response as defined in wrapper/output_format.py.

        Args:
            response: The requests response returned by `call_api`.
            query: The query dict used as defined in wrapper/input_format.py.

        Returns:
            The formatted response.
        """
        if self.result_format == "json" or self.result_format == "jsonld":
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
                utils.clean_output(record, OUTPUT_FORMAT["records"][0])

            '''
            Convert from springers format to a more usable format.
                "facets": [{
                    "name": "Name of the category",
                    "values": [{
                        "value": "Value in the category",
                        "count": "Number of occurrences of this value",
                    }],
                }],
            to:
                "facets": {
                    "category": {
                        "name": "int: counter",
                    },
                },
            See wrapper/output_format.py.
            '''
            new_facets = {}
            for facet in response.get("facets") or []:
                facet_name = facet.get("name")
                if not facet_name:
                    continue
                new_facets[facet_name] = {}
                for value in facet["values"]:
                    val_name = value.get("value")
                    if not val_name:
                        continue
                    if facet_name == "country":
                        # Convert to ISO 3166-1 alpha-2 codes
                        try:
                            iso = utils.get(pycountry.countries.search_fuzzy(val_name), 0)
                        except LookupError:
                            iso = None
                        val_name = iso.alpha_2 if iso else val_name
                    new_facets[facet_name][val_name] = int(value.get("count", 0))
            response["facets"] = new_facets

            # Delete all undefined fields
            utils.clean_output(response)

            return response

        else:
            print(f"No formatter defined for {self.result_format}. Returning raw response.")
            return response.text

    def call_api(self, query: Optional[dict] = None, raw: bool = False, dry: bool = False):
        """Make the call to the API.

        If no query is given build the manual search specified by search_field() calls.

        Args:
            query: A dictionary as defined in wrapper/input_format.py.
                If not specified, the parameters dict modified by search_field is used.
            raw: Should the raw request.Response of the query be returned?
            dry: Should only the data for the API request be returned and nothing executed?

        Returns:
            If dry is True a tuple is returned containing query-url, request-headers and -body in
                this order. This wrapper class will never return headers and a body but `None`
                instead.
            If raw is False the formatted response is returned else the raw request.Response.
        """
        if not query:
            url = self.build_query()
        else:
            url = self.translate_query(query)

        if dry:
            return url, None, None

        # Make the request and handle errors
        invalid = utils.invalid_output(
            query, url.split("&q=")[-1], self.api_key, "", self.__start_record, self.show_num
        )
        response = utils.request_error_handling(
            requests.get, {"url": url}, self.max_retries, invalid
        )
        if response is None:
            print(invalid["error"])
            return invalid
        if raw:
            return response
        return self.format_response(response, query)
