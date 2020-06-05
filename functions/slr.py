import json


def do_search(search):
    from wrapper.springerWrapper import SpringerWrapper
    from wrapper.elsevierWrapper import ElsevierWrapper

    # TODO: get API key from user account
    springer = SpringerWrapper(apiKey="***REMOVED***")
    elsevier = ElsevierWrapper(apiKey="***REMOVED***")

    db_wrappers = [elsevier]
    # db_wrappers = [springer, elsevier]

    records = []

    for db_wrapper in db_wrappers:
        first = db_wrapper.callAPI(search)

        total_results = int(first['result']['total'])

        records += first['records']

        start_points = [i for i in range(51, total_results, 50)]

        # only get 2 pages for now. Remove [:2] to get all
        for start in start_points[:2]:
            db_wrapper.startAt(start)
            results = db_wrapper.callAPI(search)
            records += results['records']

    return records


def conduct_query(review, search: dict):
    from db.connector import new_query, save_results

    query = new_query(review)

    # search in databases
    results = []
    results += do_search(search)
    # results.append(search_elsevier(search))

    save_results(results, review, query)

    review.refresh_from_db()

    return query


if __name__ == '__main__':
    from db.connector import add_review, new_query, save_results, get_results_for_query
    search_terms = {
        "search_groups": [
            {
                "search_terms": ["blockchain", "distributed ledger"],
                "match": "OR"
            }
        ],
        "match": "AND"
    }

    review = add_review("test REVIEW")
    # query = new_query(review)
    # with open('test_results.json', 'r') as file:
    #     results = json.load(file)

    query = conduct_query(review, search_terms)

    # save_results(results, review, query)

    ret = get_results_for_query(query)
    print(ret)
    pass


# for testing
def populate():
    from db.connector import add_review
    review = add_review("test_query")
    manage_query(review)
