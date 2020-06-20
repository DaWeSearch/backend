#!/usr/bin/env python3
"""A wrapper for the Elsevier API."""

from typing import Optional

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

		self.__collection = "search/sciencedirect"

		self.__startRecord = 1

		self.__numRecords = 100

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
			"metadata/article": ["application/json", "application/atom+xml", "application/xml"]
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

		self.__collection = value

	@property
	def maxRecords(self) -> int:
		"""Return the maximum number of results that the API can return."""
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
		elif self.collection == "article/metadata":
			# See https://dev.elsevier.com/tips/ArticleMetadataTips.htm
			# TODO: restrictions for pub-date, issn, isbn
			return {
				"keywords": [], "content-type": ["JL", "BS", "HB", "BK", "RW"],
				"authors": [], "affiliation": [], "pub-date": [], "title": [],
				"srctitle": [], "doi": [], "eid": [], "issn": [], "isbn": [],
				"vol-issue": [], "available-online-date": [],
				"vor-available-online-date": [], "openaccess": ["0", "1"],
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
		key = str(key).strip().lower()
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

	def buildQuery(self) -> (str, {str: str}):
		"""Build and return the url and the headers used for the query.

		Returns:
			Tuple containing the url of the endpoint and the HTTP headers for the query.
		"""
		url = self.endpoint
		url += "/" + str(self.collection)

		headers = {"X-ELS-APIKey": self.apiKey, "Accept": self.resultFormat}

		return url, headers

	def translateQuery(self, query: dict) -> {str: str}:
		"""Translate a dictionary into a query that the API understands.

		Args:
			query: A query dictionary as defined in wrapper/inputFormat.py.
		"""
		params = {}

		groups = query["search_groups"].copy()
		for i in range(len(groups)):
			groups[i] = utils.buildGroup(groups[i]["search_terms"], groups[i]["match"])
		groups = utils.buildGroup(groups, query["match"])
		try:
			self.searchField("qs", groups, parameters=params)
		except ValueError as e:
			print(e)

		return params

	def startAt(self, value: int):
		"""Set the index from which the returned results start.

		Args:
			value: The start index.
		"""
		self.__startRecord = int(value)

	def formatResponse(self, response: requests.Response, query: dict, body: {str: str}):
		"""Return the formatted response as defined in wrapper/outputFormat.py.

		Args:
			response: The requests response returned.
			query: The query dict used as defined in wrapper/inputFormat.py.
			body: The HTTP body of the query.

		Returns:
			The formatted response.
		"""
		if self.resultFormat == "application/json":
			# Load into dict
			response = response.json()

			# Modify response to fit the defined wrapper output format
			response["query"] = query
			response["dbQuery"] = body
			response["apiKey"] = self.apiKey
			response["result"] = {
				"total": response.pop("resultsFound") if "resultsFound" in response else -1,
				"start": body["display"]["offset"],
				"pageLength": body["display"]["show"],
				"recordsDisplayed": len(response["results"]) if "results" in response else 0
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
			body = self.__parameters
		else:
			body = self.translateQuery(query)

		if not body:
			raise ValueError("No search-parameters set.")
		body["display"] = {
			"offset": self.__startRecord,
			"show": self.showNum,
		}

		url, headers = self.buildQuery()

		if dry:
			return url, headers, body

		for i in range(self.maxRetries + 1):
			try:
				response = requests.put(url, headers=headers, json=body)
				response.raise_for_status()
			except requests.exceptions.HTTPError as err:
				print("HTTP error:", err)
				return utils.invalidOutput(
					query, body, self.apiKey, err, self.__startRecord, self.showNum,
				)
			except requests.exceptions.ConnectionError as err:
				print("Connection error:", err)
				return utils.invalidOutput(
					query, body, self.apiKey,
					"Failed to establish a connection: Name or service not known.",
					self.__startRecord, self.showNum,
				)
			except requests.exceptions.Timeout as err:
				# Try again
				if i < self.maxRecords:
					continue

				# Too many failed attempts
				print("Timeout error: ", err)
				return utils.invalidOutput(
					query, body, self.apiKey, "Failed to establish a connection: Timeout.",
					self.__startRecord, self.showNum,
				)
			except requests.exceptions.RequestException as err:
				print("Request error:", err)
				return utils.invalidOutput(
					query, body, self.apiKey, err, self.__startRecord, self.showNum,
				)
			# request successful
			break

		if raw:
			return response
		return self.formatResponse(response, query, body)
