#!/usr/bin/env python3

import json
from typing import Union
import urllib.parse, urllib.request
import xml.etree.ElementTree as ET

from .wrapperInterface import WrapperInterface

class SpringerWrapper(WrapperInterface):
	def __init__(self, apiKey: str):
		self.apiKey = apiKey

		self.__resultFormat = "json"

		self.__collection = "metadata"

		self.__startRecord = 1

		self.__parameters = {}

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
		# strip leading and trailing whitespace and convert to lower case
		value = str(value).strip().lower()

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
		# strip leading and trailing whitespace and convert to lower case
		value = str(value).strip().lower()

		if not value in self.allowedResultFormats:
			raise ValueError(f"Unknown collection {value}")

		# Adjusting resultFormat
		if self.resultFormat not in self.allowedResultFormats[value]:
			self.resultFormat = self.allowedResultFormats[value][0]
			print(f"Illegal resultFormat for collection. Setting to {self.resultFormat}")

		self.__collection = value

	# Maximum number of results that the API will return
	@property
	def maxRecords(self) -> int:
		if self.collection == "openaccess":
			return 20

		return 100

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

	# Dictionary of the mapping from global parameter names to local ones.
	# Also for syntax keywords like 'AND', 'OR', etc.
	@property
	def translateMap(self) -> {str: str}:
		return {
			"&&": "AND", "||": "OR", "!": "NOT",
			'"': "%22", " ": "+"
		}

	# Specify value for a given search parameter for manual search
	def searchField(self, key: str, value):
		# convert to lowercase and strip leading and trailing whitespace
		key = str(key).strip().lower()
		value = str(value).strip()
		if len(value) == 0:
			raise ValueError(f"Value is empty")

		# are key and value allowed (as combination)?
		if key in self.allowedSearchFields:
			if len(self.allowedSearchFields[key]) == 0 or value in self.allowedSearchFields[key]:
				self.__parameters[key] = value
			else:
				raise ValueError(f"Illegal value {value} for search-field {key}")
		else:
			raise ValueError(f"Searches against {key} are not supported")

	# reset all search parameters
	def resetAllFields(self):
		self.__parameters = {}

	# reset a search parameter
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
		url += "&p=" + str(self.maxRecords)

		return url

	# build a manual query from the keys and values specified by searchField
	def buildQuery(self) -> str:
		if len(self.__parameters) == 0:
			raise ValueError("No search-parameters set.")

		url = self.queryPrefix()
		url += "&q="

		for key, value in self.__parameters.items():
			url += key + ":" + urllib.parse.quote_plus(value) + "+"

		url = url[:-1]
		return url

	# translate the query from the search field on the front end into a query
	# that the API understands
	def translateQuery(self, query: str) -> str:
		url = self.queryPrefix()
		url += "&q="

		for key, value in self.translateMap.items():
			query = query.replace(key, value)

		url += query
		return url

	# Set the index from which the returned results start
	# (Necessary if there are more hits for a query than the maximum number of returned results.)
	def startAt(self, value: int):
		self.__startRecord = int(value)

	# Format raw resonse to set format
	def formatResponse(self, response: bytes, query: str):
		if self.resultFormat == "json" or self.resultFormat == "jsonld":
			response = json.loads(response)
			response["dbquery"] = response.pop("query")
			response["query"] = query
			del response["facets"]
			del response["apiMessage"]
			for record in response["records"]:
				record["uri"] = record["url"][0]["value"]
				del record["url"]
				del record["identifier"]
				authors = []
				for author in record["creators"]:
					authors.append(author["creator"])
				record["authors"] = authors
				del record["creators"]
				record["pages"] = {
					"first": record.pop("startingPage") if "startingPage" in record else "",
					"last": record.pop("endingPage") if "endingPage" in record else ""
				}
				if self.collection == "openaccess":
					record["openAccess"] = True
				else:
					record["openAccess"] = (record.pop("openaccess") == "true")

			return response

		elif self.resultFormat == "xml" or self.resultFormat == "pam":
			return ET.ElementTree(ET.fromstring(response))
		else:
			return response

	# Make the call to the API
	def callAPI(self, query: Union[str, None] = None, raw: bool = False, dry: bool = False):
		if not query:
			url = self.buildQuery()
		else:
			url = self.translateQuery(query)

		if dry:
			return url
		response = urllib.request.urlopen(url).read()
		return self.formatResponse(response, query) if not raw else response


