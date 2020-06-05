#!/usr/bin/env python3

from .wrapperInterface import WrapperInterface
from typing import Union

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

	# Specify value for a given search parameter for manual search
	def searchField(self, key: str, value):
		pass

	# Reset a search parameter
	def resetField(self, key: str):
		pass

	# Translate a search in the wrapper input format into a query that the wrapper api understands
	def translateQuery(self, query: dict) -> str:
		pass

	# Set the index from which the returned results start
	# (Necessary if there are more hits for a query than the maximum number of returned results.)
	def startAt(self, value: int):
		pass

	# Make the call to the API
	# If no query is given, use the manual search specified by searchField() calls
	def callAPI(self, query: Union[dict, None], raw: bool, dry: bool):
		pass