#!/usr/bin/env python3

import abc
from typing import Union

def error(name):
	raise NotImplementedError(f"{name} must be defined to use this base class")

class WrapperInterface(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self, apiKey: str):
		error("__init__")

	# Endpoint used for the query
	@property
	@abc.abstractmethod
	def endpoint(self) -> str:
		error("endpoint")

	# A dictionary that contains the available result formats for each collection
	@property
	@abc.abstractmethod
	def allowedResultFormats(self) -> {str: [str]}:
		error("allowedResultFormats")

	# The result format that will be used for the query
	@property
	@abc.abstractmethod
	def resultFormat(self) -> str:
		error("resultFormat")

	# resultFormat must be settable
	@resultFormat.setter
	@abc.abstractmethod
	def resultFormat(self, value: str):
		error("resultFormat (setter)")

	# Collection being used for the query
	@property
	@abc.abstractmethod
	def collection(self) -> str:
		error("collection")

	# collection must be settable
	@collection.setter
	@abc.abstractmethod
	def collection(self, value: str):
		error("collection (setter)")

	# Maximum number of results that the API will return
	@property
	@abc.abstractmethod
	def maxRecords(self) -> int:
		error("maxRecords")

	# Dictionary of allowed keys and their allowed values for searchField()
	@property
	@abc.abstractmethod
	def allowedSearchFields(self) -> {str: [str]}:
		error("allowedSearchFields")

	# Specify value for a given search parameter for manual search
	@abc.abstractmethod
	def searchField(self, key: str, value):
		error("searchField")

	# Reset a search parameter
	@abc.abstractmethod
	def resetField(self, key: str):
		error("resetField")

	# Translate a search in the wrapper input format into a query that the wrapper api understands
	@abc.abstractmethod
	def translateQuery(self, query: dict) -> str:
		error("translateQuery")

	# Set the index from which the returned results start
	# (Necessary if there are more hits for a query than the maximum number of returned results.)
	@abc.abstractmethod
	def startAt(self, value: int):
		error("startAt")

	# Make the call to the API
	# If no query is given, use the manual search specified by searchField() calls
	@abc.abstractmethod
	def callAPI(self, query: Union[dict, None], raw: bool, dry: bool):
		error("callAPI")