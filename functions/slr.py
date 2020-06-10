import os
import json


def get_api_keys():
    # TODO: get from user collection in mongodb
    springer = os.environ['SPRINGER_API_KEY']
    elsevier = os.environ['ELSEVIER_API_KEY']
    api_keys = {
        "SpringerWrapper": springer,
        "ElsevierWrapper": elsevier
    }
    return api_keys


def instantiate_wrappers():
    """
    api_keys = {
        # this is the name of the wrapper class
        "SpringerWrapper": "",
        "ElsevierWrapper": ""
    }
    """
    from wrapper import all_wrappers
    wrappers = all_wrappers

    api_keys = get_api_keys()

    instantiated_wrappers = []
    for Wrapper in wrappers:
        wrapper_name = Wrapper.__name__
        api_key = api_keys.get(wrapper_name)
        instantiated_wrappers.append(Wrapper(api_key))

    return instantiated_wrappers


def call_api(db_wrapper, search, page: int, page_length: int):
    # page 1 starts at 1, page 2 at page_length + 1
    db_wrapper.startAt((page - 1) * page_length + 1)
    db_wrapper.showNum = page_length
    return db_wrapper.callAPI(search)


def conduct_query(search, page, page_length="max"):
    """
    Get <page> number with <page_length> combined from all databases.
    Results will be divided up equally between all available literature data bases.
    """
    results = []
    db_wrappers = instantiate_wrappers()

    for db_wrapper in db_wrappers:
        if page_length == "max":
            virtual_page_length = db_wrapper.maxRecords
        else:
            virtual_page_length = int(page_length / len(db_wrappers))

        results.append(call_api(db_wrapper, search, page,
                                virtual_page_length))

    return results


def persistent_query(review, max_num_results):
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

    results = conduct_query(search, 1, 100)
    pass


    # from db.connector import update_search, add_review

    # review = add_review("test REVIEW")
    # update_search(review, search)

    # persistent_search(review, 250)