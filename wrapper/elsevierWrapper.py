#!/usr/bin/env python3
"""A wrapper for the Elsevier API."""

from copy import deepcopy
from typing import Optional, Union

import requests

from . import utils
from .outputFormat import outputFormat
from .wrapperInterface import WrapperInterface

class ElsevierWrapper(WrapperInterface):
    """A wrapper class for the Elsevier API."""

    def __init__(self, apiKey: str):
        """Initialize a wrapper object,

        Args:
            apiKey: The API key that should be used for a request.
        """
        self.apiKey = apiKey

        self.__resultFormat = "application/json"

        self.__collection = "search/scopus"

        self.__startRecord = 1

        self.__numRecords = 25

        self.__parameters = {}

        self.__maxRetries = 3

    @property
    def endpoint(self) -> str:
        """Return the endpoint used for the query."""
        return "https://api.elsevier.com/content"

    @property
    def allowedResultFormats(self) -> {str: [str]}:
        """Return a dictionary that contains the available result formats for each collection."""
        return {
            "search/sciencedirect": ["application/json"],
            "metadata/article": ["application/json", "application/atom+xml", "application/xml"],
            "search/scopus": ["application/json", "application/atom+xml", "application/xml"],
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
        # strip leading and trailing whitespace and convert to lower case
        value = str(value).strip().lower()

        if value in self.allowedResultFormats[self.collection]:
            self.__resultFormat = value
        elif ("application/" + value) in self.allowedResultFormats[self.collection]:
            print(f"Assumed you meant application/{value}")
            self.__resultFormat = "application/" + value
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
        # strip leading and trailing whitespace and convert to lower case
        value = str(value).strip().lower()

        if value not in self.allowedResultFormats:
            raise ValueError(f"Unknown collection {value}")

        if self.resultFormat not in self.allowedResultFormats.get(value):
            self.resultFormat = self.allowedResultFormats.get(value)[0]
            print("Current result format is not supported by set collection."
                    f"Setting to {self.resultFormat}.")

        self.__collection = value

        if self.maxRecords < self.showNum:
            print(f"This collection does not support requesting {self.showNum} items."
                f" Setting to {self.maxRecords}.")
            self.showNum = self.maxRecords

    @property
    def maxRecords(self) -> int:
        """Return the maximum number of results that the API can return."""
        if self.collection == "search/scopus":
            return 25
        return 100

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
        """Return all allowed search parameter, value combinations.

        An empty array means no restrictions for the value of that key.
        """
        # TODO: allow regex constraints
        if self.collection == "search/sciencedirect":
            # See https://dev.elsevier.com/tecdoc_sdsearch_migration.html
            return {
                "author": [], "date": [], "highlights": ["true", "false"],
                "openAccess": ["true", "false"], "issue": [], "loadedAfter": [],
                "page": [], "pub": [], "qs": [], "title": [], "volume": [],
            }
        elif self.collection == "metadata/article":
            # See https://dev.elsevier.com/tips/ArticleMetadataTips.htm
            # TODO: restrictions for pub-date, issn, isbn
            return {
                "keywords": [], "content-type": ["JL", "BS", "HB", "BK", "RW"],
                "authors": [], "affiliation": [], "pub-date": [], "title": [],
                "srctitle": [], "doi": [], "eid": [], "issn": [], "isbn": [],
                "vol-issue": [], "available-online-date": [],
                "vor-available-online-date": [], "openaccess": ["0", "1"],
            }
        elif self.collection == "search/scopus":
            # See https://dev.elsevier.com/tips/ScopusSearchTips.htm
            return {
                "ALL": [], "ABS": [], "AF-ID": [], "AFFIL": [], "AFFILCITY": [],
                "AFFILCOUNTRY": [], "AFFILORG": [], "ARTNUM": [], "AU-ID": [],
                "AUTHOR-NAME": [], "AUTH": [], "AUTHFIRST": [],
                "AUTHLASTNAME": [], "AUTHCOLLAB": [], "AUTHKEY": [],
                "CASREGNUMBER": [], "CHEM": [], "CHEMNAME": [], "CODE": [],
                "CONF": [], "CONFLOC": [], "CONFNAME": [], "CONFSPONSOR": [],
                "DOCTYPE": ["ar", "ab", "bk", "bz", "ch", "cp", "cr", "ed",
                "er", "le", "no", "pr", "re", "sh"],
                "PUBSTAGE": ["aip", "final"], "DOI": [], "EDFIRST": [],
                "EDITOR": [], "EDLASTNAME": [], "EISSN": [],
                "EXACTSRCTITLE": [], "FIRSTAUTH": [], "FUND-SPONSOR": [],
                "FUND-ACR": [], "FUND-NO": [], "INDEXTERMS": [], "ISBN": [],
                "ISSN": [], "ISSNP": [], "ISSUE": [], "KEY": [], "LANGUAGE": [],
                "MAUFACTURER": [], "OPENACCESS": ["0", "1"], "PAGEFIRST": [],
                "PAGELAST": [], "PAGES": [], "PMID": [], "PUBLISHER": [],
                "PUBYEAR": [], "REF": [], "REFAUTH": [], "REFTITLE": [],
                "REFSCRTITLE": [], "REFPUBYEAR": [], "REFARTNUM": [],
                "REFPAGE": [], "REFAGEFIRST": [], "SEQBANK": [],
                "SEQNUMBER": [], "SRCTITLE": [],
                "SRCTYPE": ["j", "b", "k", "p", "r", "d"], "SUBJARE": ["AGRI",
                "ARTS", "BIOC", "BUSI", "CENG", "CHEM", "COMP", "DECI", "DENT",
                "EART", "ECON", "ENER", "ENGI", "ENVI", "HEAL", "IMMU", "MATE",
                "MATH", "MEDI", "NEUR", "NURS", "PHAR", "PHYS", "PSYC", "SOCI",
                "VETE", "MULT"], "TITLE": [], "TITLE-ABS-KEY": [],
                "TITLE-ABS-KEY-AUTH": [], "TRADENAME": [], "VOLUME": [],
                "WEBSITE": [],
            }
        else:
            return {}

    @property
    def allowedDisplays(self) -> {str: [str]}:
        """Return all allowed "display" parameter, value combination.

        This is only relevant for the search/sciencedirect collection.
        An empty array means no restrictions for the value of that key.
        """
        return {
            "offset": [], "show": [], "sortBy": ["relevance", "date"],
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
        if self.collection == "search/sciencedirect":
            return {"all": "qs", "title": "title"}
        elif self.collection == "metadata/article":
            return {"keywords": "keywords", "title": "title"}
        elif self.collection == "search/scopus":
            return {
                "all": "ALL", "abstract": "ABS", "keywords": "KEY",
                "title": "TITLE",
            }
        else:
            return {}

    def searchField(self, key: str, value, parameters: Optional[dict] = None):
        """Set the value for a given search parameter in a manual search.

        Args:
            key: The search parameter.
            value: The value that the search parameter should have.
            parameters: Overrides the parameters dict used.
                Default: Internal dictionary used by callAPI when no query is given.
        """
        # (not parameters) returns True if dict is empty
        if parameters is None:
            parameters = self.__parameters

        # convert to lowercase and strip leading and trailing whitespace
        key = str(key).strip()
        value = str(value).strip()
        if len(value) == 0:
            raise ValueError(f"Value is empty")

        # are key and value allowed (as combination)?
        # TODO: allow regex constraints
        if key in self.allowedSearchFields:
            if len(self.allowedSearchFields[key]) == 0 or value in self.allowedSearchFields[key]:
                parameters[key] = value
            else:
                raise ValueError(f"Illegal value {value} for search-field {key}")
        else:
            raise ValueError(f"Searches against {key} are not supported")

    def resetField(self, key: str):
        """Reset a search parameter.

        Args:
            key: The search parameter that shall be resetted.
        """
        if key in self.__parameters:
            del self.__parameters[key]
        else:
            raise ValueError(f"Field {key} is not set.")

    def queryUrl(self) -> str:
        """Build and return the API query url without the actual search terms."""
        url = self.endpoint
        url += "/" + str(self.collection)
        if self.collection in ["metadata/article", "search/scopus"]:
            url += "?start=" + str(self.__startRecord)
            url += "&count=" + str(self.showNum)
        return url

    def queryHeaders(self) -> dict:
        """Build and return the HTTP headers used for the query."""
        return {"X-ELS-APIKey": self.apiKey, "Accept": self.resultFormat}

    def buildQuery(self) -> (str, dict, Optional[dict]):
        """Build and return a manual search from the values specified by `searchField`.

        Returns:
            A tuple containing the url, HTTP-headers and -body.
            When searching in the Metadata collection, the url will contain the search parameters
            and thus the body will be `None`.
        """
        if not self.__parameters:
            raise ValueError("No search parameters set.")

        url = self.queryUrl()
        headers = self.queryHeaders()

        if self.collection == "search/sciencedirect":
            return url, headers, self.__parameters
        elif self.collection in ["metadata/article", "search/scopus"]:
            url += "&query="
            url += utils.buildGetQuery(self.__parameters, "(", ")+AND+") + ")"
            return url, headers, None
        elif self.collection in self.allowedResultFormats:
            raise NotImplementedError(f"Cannot build query for collection {self.collection} yet.")
        else:
            raise ValueError(f"Unknown collection {self.collection}.")


    def translateQuery(self, query: dict) -> (str, dict, Optional[dict]):
        """Translate a dictionary into a query that the API understands.

        Args:
            query: A query dictionary as defined in wrapper/inputFormat.py.

        Returns:
            A tuple containing the url, HTTP-headers and -body.
            When searching in the Metadata collection, the url will contain the search parameters
            and thus the body will be `None`.

        Raises:
            ValueError:
                When unsupported values were given or there are fields in the
                dictionary missing in the query.
                Look into `wrapper/inputFormat.py` for this.
        """
        url = self.queryUrl()
        headers = self.queryHeaders()

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
                query["fields"][i] = self.fieldsTranslateMap.get(field)
            else:
                raise ValueError(f"Searching against field {field} is not supported.")

        if self.collection == "search/sciencedirect":
            params = {}

            # Build the group from the different search_terms and -groups.
            groups = query.get("search_groups", [])
            if not groups:
                raise ValueError("No search groups specified.")
            for i in range(len(groups)):
                if not groups[i].get("search_terms"):
                    raise ValueError("No search terms specified.")
                groups[i] = utils.buildGroup(groups[i]["search_terms"], groups[i].get("match"))
            groups = utils.buildGroup(groups, query.get("match"))

            # Search in every specified field.
            for field in query.get("fields"):
                self.searchField(field, groups, params)
        elif self.collection in ["metadata/article", "search/scopus"]:
            params = None
            url += "&query="
            url += utils.translateGetQuery(query, "+", "NOT", "+OR+")

        return url, headers, params

    def startAt(self, value: int):
        """Set the index from which the returned results start.

        Args:
            value: The start index.
        """
        self.__startRecord = int(value)

    def formatResponse(self, response: requests.Response, query: dict, dbQuery: Union[dict, str]):
        """Return the formatted response as defined in wrapper/outputFormat.py.

        Args:
            response: The requests response returned by `callAPI`.
            query: The query dict used as defined in wrapper/inputFormat.py.
            body: The HTTP body of the query.

        Returns:
            The formatted response.
        """
        if self.resultFormat == "application/json":
            # Load into dict
            response = response.json()

            if self.collection == "search/sciencedirect":
                # Modify response to fit the defined wrapper output format
                response["query"] = query
                response["dbQuery"] = dbQuery
                response["apiKey"] = self.apiKey
                response["result"] = {
                    "total": response.get("resultsFound", -1),
                    "start": self.__startRecord,
                    "pageLength": self.showNum,
                    "recordsDisplayed": len(response.get("results", []))
                }
                response["records"] = response.pop("results") if "results" in response else []
                for record in response.get("records") or []:
                    authors = []
                    for author in record.get("authors") or []:
                        authors.append(author["name"])
                    record["authors"] = authors
                    if "sourceTitle" in record:
                        record["publicationName"] = record.pop("sourceTitle")
                    record["publisher"] = "ScienceDirect"

                    # Delete all undefined fields
                    utils.cleanOutput(record, outputFormat["records"][0])
            elif self.collection == "metadata/article":
                # TODO!
                raise NotImplementedError("No formatter defined for the metadata collection yet.")
            elif self.collection == "search/scopus":
                response = response.get("search-results")
                if not response:
                    # We need to only fill the error message. The rest is filled like normal and the
                    # records loop will not be executed.
                    response = utils.invalidOutput(
                        *[None] * 3, "Scopus returned unknown format.", None, None
                    )
                response["query"] = query
                response["dbQuery"] = utils.get(
                    response, "opensearch:Query", "@searchTerms", default=dbQuery,
                )
                response["apiKey"] = self.apiKey
                response["result"] = {
                    "total": response.get("opensearch:totalResults", -1),
                    "start": self.__startRecord,
                    "pageLength": self.showNum,
                    "recordsDisplayed": response.get("opensearch:itemsPerPage", 0),
                }
                response["records"] = response.pop("entry") if "entry" in response else []
                for record in response.get("records"):
                    record["contentType"] = record.get("subtypeDescription")
                    record["title"] = record.get("dc:title")
                    record["authors"] = [record.get("dc:creator")]
                    record["publicationName"] = record.get("prism:publicationName")
                    record["openAccess"] = record.get("openaccess")
                    record["doi"] = record.get("prism:doi")
                    record["publisher"] = "Elsevier"
                    record["publicationDate"] = record.get("prism:coverDate")
                    record["publicationType"] = record.get("prism:aggregationType")
                    record["issn"] = record.get("prism:issn")
                    record["volume"] = record.get("prism:volume")

                    if record.get("prism:pageRange"):
                        pageRange = record.get("prism:pageRange").split("-")
                        record["pages"] = {"first": pageRange[0], "last": pageRange[1]}
                    else:
                        record["pages"] = {"first": None, "last": None}

                    for link_dict in record.get("link") or []:
                        if link_dict.get("@ref") == "scopus":
                            record["uri"] = link_dict.get("@href")
                            break

                    # Delete all undefined fields
                    utils.cleanOutput(record, outputFormat["records"][0])

            # Delete all undefined fields
            utils.cleanOutput(response)

            return response
        else:
            print(f"No formatter defined for {self.resultFormat}. Returning response body.")
            return response.text

    def callAPI(self, query: Optional[dict] = None, raw: bool = False, dry: bool = False):
        """Make the call to the API.

        If no query is given build the manual search specified by searchField() calls.

        Args:
            query: A dictionary as defined in wrapper/inputFormat.py.
                If not specified, the parameters dict modified by searchField is used.
            raw: Should the raw request.Response of the query be returned?
            dry: Should only the data for the API request be returned and nothing executed?

        Returns:
            If dry is True a tuple is returned containing query-url, request-headers and -body in
                this order. When using the collection "metadata/article" headers and body will
                always be `None`.
            If raw is False the formatted response is returned else the raw request.Response.
        """
        if not query:
            # Build from values set with `searchField`
            url, headers, body = self.buildQuery()
        else:
            # Translate given query
            url, headers, body = self.translateQuery(query)

        # Set start index and page length.
        if body:
            body["display"] = {
                "offset": self.__startRecord,
                "show": self.showNum,
            }

        if dry:
            return url, headers, body

        # Make the request and handle errors
        response = None
        reqKwargs = {"url": url, "headers": headers}

        # dbQuery will be set later because it depends on which collection is used.
        invalid = utils.invalidOutput(query, None, self.apiKey, "", self.__startRecord, self.showNum)
        reqArgs = (
            self.maxRetries,
            invalid,
        )
        if (self.collection == "search/sciencedirect"):
            reqKwargs["json"] = body
            invalid["dbQuery"] = body
            response = utils.requestErrorHandling(requests.put, reqKwargs, *reqArgs)
        elif (self.collection == "metadata/article"):
            # TODO!
            raise NotImplementedError("The metadata/article collection is not yet fully tested.")

            invalid["dbQuery"] = url.split("&query=")[-1]
            response = utils.requestErrorHandling(requests.get, reqKwargs, *reqArgs)
        elif (self.collection == "search/scopus"):
            invalid["dbQuery"] = url.split("&query=")[-1]
            response = utils.requestErrorHandling(requests.get, reqKwargs, *reqArgs)
        elif (self.collection in self.allowedResultFormats):
            invalid["error"] = f"A request to current collection {self.collection} is not yet implemented."
        else:
            invalid["error"] = f"Unknown collection {self.collection}"

        # There was an error so nothing was returned but `invalid` was modified.
        if response is None:
            print(invalid["error"])
            return invalid
        # Return raw requests.Response
        if raw:
            return response
        return self.formatResponse(response, query, invalid.get("dbQuery"))
