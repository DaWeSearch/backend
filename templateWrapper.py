#!/usr/bin/env python3

from wrapperInterface import WrapperInterface

class TemplateWrapper(WrapperInterface):
	def __init__(self, apiKey: str):
		pass

	# Endpoint used for the query
	@property
	def endpoint(self) -> str:
		pass

	# A dictionary that contains the available result formats for each collection
	@property
	def allowedResultFormats(self) -> {str: [str]}:
		pass

	# The result format that will be used for the query
	@property
	def resultFormat(self) -> str:
		pass

	# resultFormat must be settable
	@resultFormat.setter
	def resultFormat(self, value: str):
		pass

	# Collection being used for the query
	@property
	def collection(self) -> str:
		pass

	# collection must be settable
	@collection.setter
	def collection(self, value: str):
		pass

	# Maximum number of results that the API will return
	@property
	def maxRecords(self) -> int:
		pass

	# Dictionary of allowed keys and their allowed values for searchField()
	@property
	def allowedSearchFields(self) -> {str: [str]}:
		pass

	# Dictionary of the mapping from global parameter names to local ones.
	# Also for syntax keywords like 'AND', 'OR', etc.
	@property
	def translateMap(self) -> {str: str}:
		pass

	# Specify value for a given search parameter for manual search
	def searchField(self, key: str, value):
		pass

	# reset a search parameter
	def resetField(self, key: str):
		pass

	# build a manual query from the keys and values specified by searchField
	def buildQuery(self) -> str:
		pass

	# translate the query from the search field on the front end into a query
	# that the API understands
	def translateQuery(self, query: str) -> str:
		pass

	# Set the index from which the returned results start
	# (Necessary if there are more hits for a query than the maximum number of returned results.)
	def startAt(self, value: int):
		pass

	# Make the call to the API
	def callAPI(self, query: str, raw: bool, dry: bool):
		pass