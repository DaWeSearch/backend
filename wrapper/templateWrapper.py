#!/usr/bin/env python3

from .wrapperInterface import WrapperInterface
from typing import Union

class TemplateWrapper(WrapperInterface):
	def __init__(self, apiKey: str):
		pass

	@property
	def endpoint(self) -> str:
		"""Return the endpoint used for the query."""
		pass

	@property
	def allowedResultFormats(self) -> {str: [str]}:
		"""Return a dictionary that contains the available result formats for each collection."""
		pass

	@property
	def resultFormat(self) -> str:
		"""Return the result format that will be used for the query."""
		pass

	@resultFormat.setter
	def resultFormat(self, value: str):
		"""Set the result format."""
		pass

	@property
	def collection(self) -> str:
		"""Return the collection in which the query searches."""
		pass

	@collection.setter
	def collection(self, value: str):
		"""Set the collection used."""
		pass

	@property
	def maxRecords(self) -> int:
		"""Return the maximum number of results that the API can return."""
		pass

	@property
	def allowedSearchFields(self) -> {str: [str]}:
		"""Return all allowed search parameter, value combination.

		An empty array means no restrictions for the value of that key.
		"""
		pass

	def searchField(self, key: str, value):
		"""Set the value for a given search parameter in a manual search."""
		pass

	def resetField(self, key: str):
		"""Reset a search parameter."""
		pass

	def translateQuery(self, query: dict) -> str:
		"""Translate a query in the defined inputFormat into a query that the API understands."""
		pass

	def startAt(self, value: int):
		"""Set the index from which the returned results start."""
		pass

	def callAPI(self, query: Union[dict, None], raw: bool, dry: bool):
		"""Make the call to the API.

		If no query is given build the manual search specified by searchField() calls.
		"""
		pass