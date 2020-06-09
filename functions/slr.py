import json


def do_search(search, dry=False):
    # TODO: get all wrappers
    from wrapper.springerWrapper import SpringerWrapper
    from wrapper.elsevierWrapper import ElsevierWrapper

    # TODO: get API key from user account. For all dbs where a key is present, search.
    springer = SpringerWrapper(apiKey="***REMOVED***")
    elsevier = ElsevierWrapper(apiKey="***REMOVED***")

    db_wrappers = [springer]
    # db_wrappers = [springer, elsevier]

    # get info about results
    # query all databases once and get a picture of how many hits there are.
    db_info = dict()
    db_info = {
        "total": int,
        "databases": [
            "springer": {

            },
            "elsevier": {

            }
        ]
    }
    for db_wrapper in db_wrappers:
        first = db_wrapper.callAPI(search)


    records = []

    for db_wrapper in db_wrappers:
        first = db_wrapper.callAPI(search)

        total_results = int(first['result']['total'])

        records += first['records']

        page_length = int(first['result']['pageLength'])

        start_points = [i for i in range(
            page_length + 1, total_results, page_length)]

        urls = []
        # only get 2 pages for now. Remove [:2] to get all
        for start in start_points[:2]:
            db_wrapper.startAt(start)
            results = db_wrapper.callAPI(search, dry=dry)
            if dry:
                urls.append(results)
            else:
                records += results['records']

    return records

def call_api(db_wrapper, search, page: int, page_length: int):
    # page 1 starts at 1, page 2 at page_length + 1
    db_wrapper.startAt((page - 1) * page_length + 1)
    # db_wrapper.set_max_records(page_length)
    return db_wrapper.callAPI(search)


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


if __name__ == '__main__':
    from db.connector import add_review, new_query, save_results, get_results_for_review, get_review_by_id
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