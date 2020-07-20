import os
import json

# from functions.db.models import *

from wrapper import ALL_WRAPPERS
from wrapper import utils as wrapper_utils
from functions.db import models
from functions.db import connector

db_wrappers = list()


def get_api_keys():
    """Get api keys.

    TODO: get from user collection in mongodb

    Returns:
        dict of api-keys.
        dictionary keys are the same as the wrapper names defined in the wrapper module.
    """

    api_keys = dict()
    for wrapper_class in ALL_WRAPPERS:
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
    for wrapper_class in ALL_WRAPPERS:
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
        db_wrapper: object that implements the wrapper interface defined in wrapper/wrapper_interface.py
        search: dict of search terms as defined in wrapper/input_format.py
        page: page number
        page_length: length of page

    Returns:
        results as specified in wrapper/ouputFormat.py
    """
    # page 1 starts at 1, page 2 at page_length + 1
    db_wrapper.start_at((page - 1) * page_length + 1)
    db_wrapper.show_num = page_length
    return db_wrapper.call_api(search)


def conduct_query(search: dict, page: int, page_length="max") -> list:
    """Get page of specific length. Aggregates results from all available literature data bases.

    The number of results from each data base will be n/page_length with n being the number of data bases.

    Args:
        search: dict of search terms as defined in wrapper/input_format.py
        page: page number
        page_length: length of page. If set to "max", the respective maxmimum number of results
            results is returned by each wrapper.

    Returns:
        list of results in format https://github.com/DaWeSys/backend/blob/simple_persistance/wrapper/output_format.py.
            one for each wrapper.
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
            virtual_page_length = db_wrapper.max_records
        else:
            virtual_page_length = int(page_length / len(db_wrappers))

        results.append(
            call_api(
                db_wrapper, search, page, virtual_page_length
            )
        )

    results[0]["facets"] = wrapper_utils.combine_facets([res.get("facets") for res in results])
    for res in results[1:]:
        res["facets"] = {
            "countries": {},
            "keywords": [],
        }

    return results


def results_persisted_in_db(results: list, review: models.Review) -> list:
    """Mark all records that are already persisted in our data base.

    Args:
        results: a list of results as returned by conduct_query.
            [{<result as described in wrapper/output_format.py>}, {<..    def test_pagination_for_review(self):
        page1 = get_page_results_for_review(self.review, 1, 10)
        self.assertTrue(len(page1) == 10)

        page2 = get_page_results_for_review(self.review, 2, 10)
        self.assertTrue(len(page2) == 10)

        self.assertNotEqual(page1, page2).>}]
        review: review object

    Returns:
        the same list with the additional field "persisted" for each record.
    """
    persisted_dois = connector.get_dois_for_review(review)

    combined = []
    for wrapper_results in results:
        wrapper_combined = []
        for wrapper_result in wrapper_results.get('records'):
            doi = wrapper_result.get('doi')
            if doi in persisted_dois:
                wrapper_result['persisted'] = True
            else:
                wrapper_result['persisted'] = False
            wrapper_combined.append(wrapper_result)

        wrapper_results['records'] = wrapper_combined
        combined.append(wrapper_results)

    return combined


def persistent_query(query: models.Query, review: models.Review, max_num_results: int):
    """Conduct a query and persist it. Query until max_num_results is reached (at the end of the query).

    Args:
        query: query-object
        max_num_results: roughly the maxmimum number of results (may overshoot a little)

    Returns:
        TODO: maybe this could return the first page of results only?? This behavior needs to be defined
    """
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

            connector.save_results(result.get('records'), review, query)


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

    review = connector.get_review_by_id("5ecd4bc497446f15f0a85f0d")

    # review = connector.update_search(review, search)

    # query = connector.new_query(review)
    # persistent_query(review, query, 100)

    results = conduct_query(search, 5, 100)
    results = results_persisted_in_db(results, review)

    pass

    # # sample usage of persistent query
    # from functions.db.connector import update_search, add_review

    # review = add_review("test REVIEW")
    # update_search(review, search)

    # # persistent_search(review, 250)
