import os
import json


def get_wrappers():
    # TODO: get from wrapper interface lib
    from wrapper.springerWrapper import SpringerWrapper
    from wrapper.elsevierWrapper import ElsevierWrapper

    return [SpringerWrapper, ElsevierWrapper]


def get_api_keys():
    # TODO: get from user collection from mongodb
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
    api_keys = get_api_keys()
    wrappers = get_wrappers()

    instantiated_wrappers = []
    for Wrapper in wrappers:
        wrapper_name = Wrapper.__name__
        api_key = api_keys.get(wrapper_name)
        instantiated_wrappers.append(Wrapper(api_key))

    return instantiated_wrappers


def call_api(db_wrapper, search, page: int, page_length: int):
    # page 1 starts at 1, page 2 at page_length + 1
    db_wrapper.startAt((page - 1) * page_length + 1)
    # db_wrapper.set_max_records(page_length)
    return db_wrapper.callAPI(search)


def do_search(search, page, page_length):
    """
    search: search dict
    pages: [1, 2, 3, 4]
    """


    # get info about results
    # query all databases once and get a picture of how many hits there are.
    db_info = dict()
    # db_info = {
    #     "total": int,
    #     "databases": [
    #         "springer": {

    #         },
    #         "elsevier": {

    #         }
    #     ]
    # }
    results = []
    total_page_length = 100

    db_wrappers = instantiate_wrappers()
    # one page
    page = 1
    page_length = int(total_page_length / len(db_wrappers))


    for db_wrapper in db_wrappers:
        results.append(call_api(db_wrapper, search, page, page_length))

    # calc total results
    total = 0
    for res in results:
        total += res['result']['total']

    return results


if __name__ == '__main__':
    search = {
        "search_groups": [
            {
                "search_terms": ["blockchain", "distributed ledger"],
                "match": "OR"
            }
        ],
        "match": "AND"
    }

    do_search(search)

# option a: search just in data base
#   - total results for each db and combined total
#   - get page (a few hits from each db for every page)
# option b: get x results from data base
#   - set proportions (default: 1/n)
#
# input:
#   - how many results to get
# output:
#   - records
#   - meta: total results, results returned


def conduct_query(review, search: dict):
    from db.connector import new_query, save_results

    query = new_query(review)

    # search in databases
    results = []
    results += do_search(search, dry=False)
    # results.append(search_elsevier(search))

    save_results(results, review, query)

    review.refresh_from_db()

    return query


# if __name__ == '__main__':
#     pass
#     from db.connector import add_review, new_query, save_results, get_results_for_review, get_review_by_id
    # search_terms = {
    #     "search_groups": [
    #         {
    #             "search_terms": ["blockchain", "distributed ledger"],
    #             "match": "OR"
    #         }
    #     ],
    #     "match": "AND"
    # }

    # review = add_review("test REVIEW")

    # query = conduct_query(review, search_terms)

    # review = get_review_by_id("5ede4708cfb4b32044d32734")
    # res = get_results_for_review(review, page=1, page_length=50)

    #
    # for db_wrapper in db_wrappers:
    #     first = db_wrapper.callAPI(search)

    #     total_results = int(first['result']['total'])

    #     records += first['records']

    #     page_length = int(first['result']['pageLength'])

    #     start_points = [i for i in range(
    #         page_length + 1, total_results, page_length)]

    #     urls = []
    #     # only get 2 pages for now. Remove [:2] to get all
    #     for start in start_points[:2]:
    #         db_wrapper.startAt(start)
    #         results = db_wrapper.callAPI(search, dry=dry)
    #         if dry:
    #             urls.append(results)
    #         else:
    #             records += results['records']
