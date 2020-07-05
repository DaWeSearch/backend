#!/usr/bin/env python3
"""The interface that every wrapper has to implement."""

import abc
from typing import Optional

def error(name):
    """Raise an error.

    Args:
        name: Name of the function that will appear in the error message.

    Raises:
        NotImplementedError: always.
    """
    raise NotImplementedError(f"{name} must be defined to use this base class")

class WrapperInterface(metaclass=abc.ABCMeta):
    """The interface class that every wrapper has to implement."""

    @abc.abstractmethod
    def __init__(self, apiKey: str):
        """Initialize a wrapper object.

        Args:
            apiKey: The API key that should be used for a request.
        """
        error("__init__")

    @property
    @abc.abstractmethod
    def endpoint(self) -> str:
        """Return the endpoint used for the query."""
        error("endpoint")

    @property
    @abc.abstractmethod
    def allowed_result_formats(self) -> {str: [str]}:
        """Return a dictionary that contains the available result formats for each collection."""
        error("allowed_result_formats")

    @property
    @abc.abstractmethod
    def result_format(self) -> str:
        """Return the result format that will be used for the query."""
        error("result_format")

    @result_format.setter
    @abc.abstractmethod
    def result_format(self, value: str):
        """Set the result format.

        Args:
            value: The result format that will be set. Has to be allowed for set collection.
        """
        error("result_format (setter)")

    @property
    @abc.abstractmethod
    def collection(self) -> str:
        """Return the collection in which the query searches."""
        error("collection")

    @collection.setter
    @abc.abstractmethod
    def collection(self, value: str):
        """Set the collection used.

        Args:
            value: The collection that will be set. Has to be an allowed value.
        """
        error("collection (setter)")

    @property
    @abc.abstractmethod
    def max_records(self) -> int:
        """Return the maximum number of results that the API can return."""
        error("max_records")

    @property
    def show_num(self) -> int:
        """Return the number of results that the API will return."""
        error("show_num")

    @show_num.setter
    def show_num(self, value: int):
        """Set the number of results that will be returned.

        Args:
            value: The number of results.
        """
        error("show_num (setter)")

    @property
    @abc.abstractmethod
    def allowed_search_fields(self) -> {str: [str]}:
        """Return all allowed search parameter, value combination.

        An empty array means no restrictions for the value of that key.
        """
        error("allowed_search_fields")

    @property
    def max_retries(self) -> int:
        """Return the maximum number of retries the wrapper will do on a timeout."""
        error("max_retries")

    @max_retries.setter
    def max_retries(self, value: int):
        """Set maximum number of retries on a timeout.

        Args:
            value: Number of retries that will be set.
        """
        error("max_retries (setter)")

    @property
    def property_translate_map(self) -> dict:
        """Return the translate map for the fields field of the input format."""
        error("property_translate_map")

    @abc.abstractmethod
    def search_field(self, key: str, value):
        """Set the value for a given search parameter in a manual search.

        Args:
            key: The search parameter.
            value: The value that the search parameter should have.
        """
        error("search_field")

    @abc.abstractmethod
    def reset_field(self, key: str):
        """Reset a search parameter.

        Args:
            key: The search parameter that shall be resetted.
        """
        error("reset_field")

    @abc.abstractmethod
    def translate_query(self, query: dict) -> str:
        """Translate a dictionary into a query that the API understands.

        Args:
            query: A query dictionary as defined in wrapper/input_format.py.
        """
        error("translate_query")

    @abc.abstractmethod
    def start_at(self, value: int):
        """Set the index from which the returned results start.

        Args:
            value: The start index.
        """
        error("start_at")

    @abc.abstractmethod
    def call_api(self, query: Optional[dict] = None, raw: bool = False, dry: bool = False):
        """Make the call to the API.

        If no query is given build the manual search specified by search_field() calls.

        Args:
            query: A dictionary as defined in wrapper/input_format.py.
                If not specified, the parameters dict modified by search_field is used.
            raw: Should the raw request.Response of the query be returned?
            dry: Should only the data for the API request be returned and nothing executed?

        Returns:
            If dry is True a tuple is returned containing query-url, request-headers and -body in
                this order.
            If raw is False the formatted response is returned else the raw request.Response.
        """
        error("call_api")
