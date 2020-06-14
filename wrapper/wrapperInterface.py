#!/usr/bin/env python3

import abc
from typing import Union

def error(name):
	raise NotImplementedError(f"{name} must be defined to use this base class")

class WrapperInterface(metaclass=abc.ABCMeta):
	@abc.abstractmethod
	def __init__(self, apiKey: str):
		error("__init__")

	@property
	@abc.abstractmethod
	def endpoint(self) -> str:
		"""Return the endpoint used for the query."""
		error("endpoint")

	@property
	@abc.abstractmethod
	def allowedResultFormats(self) -> {str: [str]}:
		"""Return a dictionary that contains the available result formats for each collection."""
		error("allowedResultFormats")

	@property
	@abc.abstractmethod
	def resultFormat(self) -> str:
		"""Return the result format that will be used for the query."""
		error("resultFormat")

	@resultFormat.setter
	@abc.abstractmethod
	def resultFormat(self, value: str):
		"""Set the result format."""
		error("resultFormat (setter)")

	@property
	@abc.abstractmethod
	def collection(self) -> str:
		"""Return the collection in which the query searches."""
		error("collection")

	@collection.setter
	@abc.abstractmethod
	def collection(self, value: str):
		"""Set the collection used."""
		error("collection (setter)")

	@property
	@abc.abstractmethod
	def maxRecords(self) -> int:
		"""Return the maximum number of results that the API can return."""
		error("maxRecords")

	@property
	@abc.abstractmethod
	def allowedSearchFields(self) -> {str: [str]}:
		"""Return all allowed search parameter, value combination.

		An empty array means no restrictions for the value of that key.
		"""
		error("allowedSearchFields")

	@abc.abstractmethod
	def searchField(self, key: str, value):
		"""Set the value for a given search parameter in a manual search."""
		error("searchField")

	@abc.abstractmethod
	def resetField(self, key: str):
		"""Reset a search parameter."""
		error("resetField")

	@abc.abstractmethod
	def translateQuery(self, query: dict) -> str:
		"""Translate a query in the defined inputFormat into a query that the API understands."""
		error("translateQuery")

	@abc.abstractmethod
	def startAt(self, value: int):
		"""Set the index from which the returned results start."""
		error("startAt")

	@abc.abstractmethod
	def callAPI(self, query: Union[dict, None], raw: bool, dry: bool):
		"""Make the call to the API.

		If no query is given build the manual search specified by searchField() calls.
		"""
		error("callAPI")