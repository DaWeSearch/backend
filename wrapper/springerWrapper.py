#!/usr/bin/env python3

from typing import Optional
import urllib.parse

import requests

from . import utils
from .outputFormat import outputFormat
from .wrapperInterface import WrapperInterface

class SpringerWrapper(WrapperInterface):
	def __init__(self, apiKey: str):
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
		"""Set the result format."""
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
		"""Set the collection used."""
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
		"""Set the number of results that will be returned."""
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
		"""Set maximum number of retries on a timeout."""
		self.__maxRetries = value

	def searchField(self, key: str, value):
		"""Set the value for a given search parameter in a manual search."""
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
		"""Reset a search parameter."""
		if key in self.__parameters:
			del self.__parameters[key]
		else:
			raise ValueError(f"Field {key} is not set.")

	def queryPrefix(self) -> str:
		"""Build and return the API query without the acutuall search terms."""
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

		# Add url encoded key, value pair to query
		for key, value in self.__parameters.items():
			url += key + ":" + urllib.parse.quote_plus(value) + "+"

		url = url[:-1]
		return url

	def translateQuery(self, query: dict) -> str:
		"""Translate a query in the defined inputFormat into a query that the API understands."""
		url = self.queryPrefix()
		url += "&q="

		groups = query["search_groups"].copy()
		for i in range(len(groups)):
			for j in range(len(groups[i]["search_terms"])):
				term = groups[i]["search_terms"][j]

				# Enclose seach term in quotes if it contains a space to prevent splitting
				if " " in term:
					term = '"' + term + '"'

				# Urlencode search term
				groups[i]["search_terms"][j] = urllib.parse.quote(term)

			groups[i] = utils.buildGroup(groups[i]["search_terms"], groups[i]["match"], "+", "-")
		url += utils.buildGroup(groups, query["match"], "+", "-")

		return url

	def startAt(self, value: int):
		"""Set the index from which the returned results start."""
		self.__startRecord = int(value)

	def formatResponse(self, response: requests.Response, query: str):
		"""Return the formatted response tht conforms to the defined outputFormat."""
		if self.resultFormat == "json" or self.resultFormat == "jsonld":
			# Load into dict
			response = response.json()

			# Modify response to fit the defined wrapper output format
			response["dbQuery"] = response.pop("query")
			response["query"] = query
			response["result"] = response.pop("result")[0]
			for record in response["records"]:
				record["uri"] = record["url"][0]["value"]
				authors = []
				for author in record["creators"]:
					authors.append(author["creator"])
				record["authors"] = authors
				record["pages"] = {
					"first": record.pop("startingPage") if "startingPage" in record else "",
					"last": record.pop("endingPage") if "endingPage" in record else ""
				}
				if self.collection == "openaccess":
					record["openAccess"] = True
				else:
					record["openAccess"] = (record.pop("openaccess") == "true")

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
		"""
		if not query:
			url = self.buildQuery()
		else:
			url = self.translateQuery(query)

		if dry:
			return url

		# Make the request and handle errors
		dbQuery = url.split("&q=")[-1]
		for i in range(self.maxRetries + 1):
			try:
				response = requests.get(url)
				# raise a HTTPError if the status code suggests an error
				response.raise_for_status()
			except requests.exceptions.HTTPError as err:
				print("HTTP error:", err)
				return utils.invalidOutput(
					query, dbQuery, self.apiKey, err, self.__startRecord, self.showNum,
				)
			except requests.exceptions.ConnectionError as err:
				print("Connection error:", err)
				return utils.invalidOutput(
					query, dbQuery, self.apiKey,
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
					query, dbQuery, self.apiKey, "Failed to establish a connection: Timeout.",
					self.__startRecord, self.showNum,
				)
			except requests.exceptions.RequestException as err:
				print("Request error:", err)
				return utils.invalidOutput(
					query, dbQuery, self.apiKey, err, self.__startRecord, self.showNum,
				)
			# request successful
			break

		if raw:
			return response
		return self.formatResponse(response, query)
