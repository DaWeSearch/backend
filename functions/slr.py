import os
import json

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
    springer = os.getenv('SPRINGER_API_KEY')
    elsevier = os.getenv('ELSEVIER_API_KEY')
    api_keys = {
        "SpringerWrapper": springer,
        "ElsevierWrapper": elsevier
    }
    return api_keys


def instantiate_wrappers():
    """Instantiate wrappers with api keys.

    Returns:
        list of instantiated wrapper objects, each for each data base wrapper
    """
    wrappers = all_wrappers

    api_keys = get_api_keys()

    instantiated_wrappers = []
    for Wrapper in wrappers:
        wrapper_name = Wrapper.__name__
        api_key = api_keys.get(wrapper_name)
        instantiated_wrappers.append(Wrapper(api_key))

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

    for db_wrapper in db_wrappers:
        if page_length == "max":
            virtual_page_length = db_wrapper.maxRecords
        else:
            virtual_page_length = int(page_length / len(db_wrappers))

        results.append(call_api(db_wrapper, search, page,
                                virtual_page_length))

    return results


def persistent_query(review: Review, max_num_results: int):
    """Conduct a query and persist it. Query until max_num_results is reached (at the end of the query).

    Args:
        review: review-object
        max_num_results: roughly the maxmimum number of results (may overshoot a little)

    Returns:
        TODO: maybe this could return the first page of results only?? This behavior needs to be defined
    """
    from db.connector import save_results, new_query

    query = new_query(review)

    num_results = 0
    page = 1
    search = review.search.to_son().to_dict()
    while num_results < max_num_results:
        results = conduct_query(search, page)

        for result in results:
            num_results += int(result.get('result').get('recordsDisplayed'))

            save_results(result.get('records'), review, query)


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
    results = conduct_query(search, 1, 100)
    pass

    # sample usage of persistent query
    from db.connector import update_search, add_review

    review = add_review("test REVIEW")
    update_search(review, search)

    # persistent_search(review, 250)
