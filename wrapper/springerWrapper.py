#!/usr/bin/env python3

from typing import Union
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

	# Endpoint used for the query
	@property
	def endpoint(self) -> str:
		return "http://api.springernature.com"

	# A dictionary that contains the available result formats for each collection
	@property
	def allowedResultFormats(self) -> {str: [str]}:
		return {
			"meta/v2": ["pam", "jats", "json", "jsonp", "jsonld"],
			"metadata": ["pam", "json", "jsonp"],
			"openaccess": ["jats", "json", "jsonp"],
			"integro": ["xml"]
		}

	# The result format that will be used for the query
	@property
	def resultFormat(self) -> str:
		return self.__resultFormat

	# resultFormat must be settable
	@resultFormat.setter
	def resultFormat(self, value: str):
		# Strip leading and trailing whitespace and convert to lower case
		value = str(value).strip().lower()

		# Check if the format is supported by the selected collection
		if value in self.allowedResultFormats[self.collection]:
			self.__resultFormat = value
		else:
			raise ValueError(f"Illegal format {value} for collection {self.collection}")

	# Collection being used for the query
	@property
	def collection(self) -> str:
		return self.__collection

	# collection must be settable
	@collection.setter
	def collection(self, value: str):
		# Strip leading and trailing whitespace and convert to lower case
		value = str(value).strip().lower()

		if value not in self.allowedResultFormats:
			raise ValueError(f"Unknown collection {value}")

		# Adjust resultFormat
		if self.resultFormat not in self.allowedResultFormats[value]:
			self.resultFormat = self.allowedResultFormats[value][0]
			print(f"Illegal resultFormat for collection. Setting to {self.resultFormat}")

		self.__collection = value

	# Maximum number of results that the API can return
	@property
	def maxRecords(self) -> int:
		if self.collection == "openaccess":
			return 20

		return 50

	# Number of results that the API will return
	@property
	def showNum(self) -> int:
		return self.__numRecords

	# Set the number of results returned
	@showNum.setter
	def showNum(self, value: int):
		if value > self.maxRecords:
			print(f"{value} exceeds maximum of {self.maxRecords}. Set to maximum.")
			self.__numRecords = self.maxRecords
		else:
			self.__numRecords = value

	# Dictionary of allowed keys and their allowed values for searchField()
	@property
	def allowedSearchFields(self) -> {str: [str]}:
		return {
			"doi":[], "subject":[], "keyword":[], "pub":[], "year":[],
			"onlinedate":[], "onlinedatefrom":[], "onlinedateto": [],
			"country":[], "isbn":[], "issn":[], "journalid":[],
			"topicalcollection":[], "journalonlinefirst":["true"],
			"date":[], "issuetype":[], "issue":[], "volume":[],
			"type":["Journal", "Book"]
		}

	# Maximum number of retries on a timeout
	@property
	def maxRetries(self) -> int:
		return self.__maxRetries

	# Set maximum number of retries on a timeout
	@maxRetries.setter
	def maxRetries(self, value: int):
		self.__maxRetries = value

	# Specify value for a given search parameter for manual search
	def searchField(self, key: str, value):
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

	# Reset all search parameters
	def resetAllFields(self):
		self.__parameters = {}

	# Reset a search parameter
	def resetField(self, key: str):
		if key in self.__parameters:
			del self.__parameters[key]
		else:
			raise ValueError(f"Field {key} is not set.")

	# Build API query without the search terms
	def queryPrefix(self) -> str:
		url = self.endpoint
		url += "/" + str(self.collection)
		url += "/" + str(self.resultFormat)
		url += "?api_key=" + str(self.apiKey)
		url += "&s=" + str(self.__startRecord)
		url += "&p=" + str(self.showNum)

		return url

	# Build a manual query from the keys and values specified by searchField
	def buildQuery(self) -> str:
		if len(self.__parameters) == 0:
			raise ValueError("No search-parameters set.")

		url = self.queryPrefix()
		url += "&q="

		# Add url encoded key, value pair to query
		for key, value in self.__parameters.items():
			url += key + ":" + urllib.parse.quote_plus(value) + "+"

		url = url[:-1]
		return url

	# Translate a search in the wrapper input format into a query that the wrapper api understands
	def translateQuery(self, query: dict) -> str:
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

	# Set the index from which the returned results start
	# (Necessary if there are more hits for a query than the maximum number of returned results.)
	def startAt(self, value: int):
		self.__startRecord = int(value)

	# Format raw resonse to set format
	def formatResponse(self, response: requests.Response, query: str):
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

	# Make the call to the API
	# If no query is given, use the manual search specified by searchField() calls
	def callAPI(self, query: Union[dict, None] = None, raw: bool = False, dry: bool = False):
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


