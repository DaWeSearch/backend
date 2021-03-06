"""A wrapper for the <DATABASE> API."""

from typing import Optional

from .wrapper_interface import WrapperInterface

class TemplateWrapper(WrapperInterface):
    """A wrapper class for the <DATABASE> API."""

    def __init__(self, api_key: str):
        """Initialize a wrapper object.

        Args:
            api_key: The API key that should be used for a request.
        """
        pass

    @property
    def endpoint(self) -> str:
        """Return the endpoint used for the query."""
        pass

    @property
    def allowed_result_formats(self) -> {str: [str]}:
        """Return a dictionary that contains the available result formats for each collection."""
        pass

    @property
    def result_format(self) -> str:
        """Return the result format that will be used for the query."""
        pass

    @result_format.setter
    def result_format(self, value: str):
        """Set the result format.

        Args:
            value: The result format that will be set. Has to be allowed for set collection.
        """
        pass

    @property
    def collection(self) -> str:
        """Return the collection in which the query searches."""
        pass

    @collection.setter
    def collection(self, value: str):
        """Set the collection used.

        Args:
            value: The collection that will be set. Has to be an allowed value.
        """
        pass

    @property
    def max_records(self) -> int:
        """Return the maximum number of results that the API can return."""
        pass

    @property
    def show_num(self) -> int:
        """Return the number of results that the API will return."""
        pass

    @show_num.setter
    def show_num(self, value: int):
        """Set the number of results that will be returned.

        Args:
            value: The number of results.
        """
        pass

    @property
    def allowed_search_fields(self) -> {str: [str]}:
        """Return all allowed search parameter, value combination.

        An empty array means no restrictions for the value of that key.
        """
        pass

    @property
    def max_retries(self) -> int:
        """Return the maximum number of retries the wrapper will do on a timeout."""
        pass

    @max_retries.setter
    def max_retries(self, value: int):
        """Set maximum number of retries on a timeout.

        Args:
            value: Number of retries that will be set.
        """
        pass

    @property
    def property_translate_map(self) -> dict:
        """Return the translate map for the fields field of the input format."""
        pass

    def search_field(self, key: str, value):
        """Set the value for a given search parameter in a manual search.

        Args:
            key: The search parameter.
            value: The value that the search parameter should have.
        """
        pass

    def reset_field(self, key: str):
        """Reset a search parameter.

        Args:
            key: The search parameter that shall be resetted.
        """
        pass

    def translate_query(self, query: dict) -> str:
        """Translate a dictionary into a query that the API understands.

        Args:
            query: A query dictionary as defined in wrapper/input_format.py.
        """
        pass

    def start_at(self, value: int):
        """Set the index from which the returned results start.

        Args:
            value: The start index. (1-based)
        """
        pass

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
        pass
