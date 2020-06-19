import os
import json

# from functions.db.models import *
from functions.db.models import Review, Query
from wrapper import all_wrappers

db_wrappers = list()

def get_api_keys():
    """Get api keys.

    TODO: get from user collection in mongodb

    Returns:
        dict of api-keys.
        dictionary keys are the same as the wrapper names defined in the wrapper module.
    """
    # TODO: get from user collection in mongodb

    api_keys = dict()
    for wrapper_class in all_wrappers:
        # remove Wrapper suffix from class name
        var_name = wrapper_class.__name__
        if var_name.endswith('Wrapper'):
            var_name = var_name[:-7]

        # bring in env var format
        var_name = var_name.upper()
        var_name += "_API_KEY"

        api_keys[wrapper_class.__name__] = os.getenv(var_name)

    return api_keys


def instantiate_wrappers():
    """Instantiate wrappers with api keys.

    Returns:
        list of instantiated wrapper objects, each for each data base wrapper
    """
    api_keys = get_api_keys()

    instantiated_wrappers = []
    for wrapper_class in all_wrappers:
        wrapper_name = wrapper_class.__name__
        api_key = api_keys.get(wrapper_name)
        if api_key:
            instantiated_wrappers.append(wrapper_class(api_key))
        else:
            print(f"No API key specified for {wrapper_class.__name__}.")

    return instantiated_wrappers


def call_api(db_wrapper, search: dict, page: int, page_length: int):
    """Call literature data base wrapper to query for a specific page.

    Args:
        db_wrapper: object that implements the wrapper interface defined in wrapper/wrapperInterface.py
        search: dict of search terms as defined in wrapper/inputFormat.py
        page: page number
        page_length: length of page

    Returns:
        results as specified in wrapper/ouputFormat.py
    """
    # page 1 starts at 1, page 2 at page_length + 1
    db_wrapper.startAt((page - 1) * page_length + 1)
    db_wrapper.showNum = page_length
    return db_wrapper.callAPI(search)


def conduct_query(search: dict, page: int, page_length="max"):
    """Get page of specific length. Aggregates results from all available literature data bases.

    The number of results from each data base will be n/page_length with n being the number of data bases.

    Args:
        search: dict of search terms as defined in wrapper/inputFormat.py
        page: page number
        page_length: length of page. If set to "max", the respective maxmimum number of results
            results is returned by each wrapper.
    """
    global db_wrappers
    results = []

    if not db_wrappers:
        db_wrappers = instantiate_wrappers()

    if len(db_wrappers) == 0:
        print("No wrappers existing.")
        return []

    for db_wrapper in db_wrappers:
        if page_length == "max":
            virtual_page_length = db_wrapper.maxRecords
        else:
            virtual_page_length = int(page_length / len(db_wrappers))

        results.append(
            call_api(
                db_wrapper, search, page, virtual_page_length
            )
        )

    return results


def persistent_query(query: Query, max_num_results: int):
    """Conduct a query and persist it. Query until max_num_results is reached (at the end of the query).

    Args:
        query: query-object
        max_num_results: roughly the maxmimum number of results (may overshoot a little)

    Returns:
        TODO: maybe this could return the first page of results only?? This behavior needs to be defined
    """
    from functions.db.connector import save_results

    num_results = 0
    page = 1
    search = query.search.to_son().to_dict()

    while num_results < max_num_results:
        results = conduct_query(search, page)

        if not results:
            print("Part of the query returned no results. Aborting.")
            return

        for result in results:
            num_results += int(result.get('result').get('recordsDisplayed'))

            save_results(result.get('records'), query)


if __name__ == '__main__':
    search = {
        "search_groups": [
            {
                "search_terms": ["bitcoin"],
                "match": "OR"
            }
        ],
        "match": "AND"
    }
    # sample usage of dry search
    #results = conduct_query(search, 1, 100)
    pass

    # sample usage of persistent query
    from functions.db.connector import add_review, new_query

    review = add_review("test REVIEW")
    query = new_query(review, search)
    persistent_query(query, 250)
